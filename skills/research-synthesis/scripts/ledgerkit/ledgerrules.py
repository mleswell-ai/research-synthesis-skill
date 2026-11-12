"""Rules applied to the ledger itself: structure, protocol, evidence links, certainty
ceilings and verification state."""

from __future__ import annotations

from .ceiling import claim_ceiling, required_checks
from .issues import Issue
from .schema import (ACCESS, CHECK_STATES, CLAIM_ID, CLAIM_TYPES, CORPORA, DERIVED_TYPES, EVIDENCE_KINDS,
                     ISO_DATE, LEVELS, MODES, SOURCE_ID, SOURCE_TYPES, STATUSES, Ledger, blank, level)

# A quotation beyond this length is usually better paraphrased.
LONG_QUOTE = 300
# With fewer included sources than this, a lack of recorded disagreement is unremarkable.
DISSENT_EXPECTED_FROM = 5


def _allowed(values) -> str:
    return ", ".join(values)


def header_rules(ledger: Ledger) -> list[Issue]:
    out = []
    for name in ("question", "as_of", "mode", "protocol", "sources", "claims"):
        if blank(ledger.data.get(name)):
            out.append(Issue("S01", "ledger", f"'{name}' is missing or empty."))
    if ledger.mode is not None and ledger.mode not in MODES:
        out.append(Issue("S01", "ledger", f"mode '{ledger.mode}' is not one of: {_allowed(MODES)}."))
    as_of = ledger.data.get("as_of")
    if isinstance(as_of, str) and as_of.strip() and not ISO_DATE.match(as_of):
        out.append(Issue("S01", "ledger", f"as_of '{as_of}' is not a date in YYYY-MM-DD form."))
    return out


def protocol_rules(ledger: Ledger) -> list[Issue]:
    out = []
    if not ledger.protocol:
        return out
    corpus = ledger.protocol.get("corpus")
    if corpus not in CORPORA:
        out.append(Issue("P01", "protocol", f"corpus is {corpus!r}; expected one of: {_allowed(CORPORA)}."))
    log = ledger.protocol.get("search_log")
    entries = [e for e in log if isinstance(e, dict) and not blank(e.get("query"))] if isinstance(log, list) else []
    searched = corpus in ("searched", "mixed")
    if ledger.mode == "systematic":
        if blank(ledger.protocol.get("inclusion")):
            out.append(Issue("P02", "protocol", "no inclusion criteria recorded."))
        if searched and not entries:
            out.append(Issue("P03", "protocol", "no searches logged."))
    elif searched and not entries:
        out.append(Issue("P04", "protocol", "no searches logged."))
    for n, entry in enumerate(entries, start=1):
        missing = [f for f in ("where", "date") if blank(entry.get(f))]
        if missing:
            out.append(Issue("P05", f"search {n}", f"missing {' and '.join(missing)}."))
    return out


def source_rules(ledger: Ledger) -> list[Issue]:
    out = []
    seen = set()
    for n, src in enumerate(ledger.raw_sources, start=1):
        if not isinstance(src, dict):
            out.append(Issue("S03", f"sources entry {n}", "is not an object."))
            continue
        sid = src.get("id")
        if not isinstance(sid, str) or not SOURCE_ID.match(sid):
            out.append(Issue("S02", f"sources entry {n}", f"id {sid!r} should look like S1 or SA1."))
            continue
        if sid in seen:
            out.append(Issue("S02", sid, "this id is used by more than one source."))
            continue
        seen.add(sid)
        for name in ("title", "year", "ref", "type", "access", "status"):
            if blank(src.get(name)) or src.get(name) == 0:
                hint = " Use \"n.d.\" when undated." if name == "year" else ""
                out.append(Issue("S03", sid, f"'{name}' is missing.{hint}"))
        for name, allowed in (("type", SOURCE_TYPES), ("access", ACCESS), ("status", STATUSES)):
            value = src.get(name)
            if not blank(value) and value not in allowed:
                out.append(Issue("S03", sid, f"{name} '{value}' is not one of: {_allowed(allowed)}."))
        if src.get("status") == "excluded" and blank(src.get("exclusion_reason")):
            out.append(Issue("S04", sid, "add an exclusion_reason."))
        if src.get("status") == "included":
            if blank(src.get("lineage")):
                out.append(Issue("S05", sid, "no lineage. Give sources that report the same study, dataset "
                                             "or original the same lineage (L1, L2, ...)."))
            rating = ledger.appraisal(sid)
            if rating not in LEVELS:
                out.append(Issue("S05", sid, f"appraisal.rating must be one of: {_allowed(LEVELS)}."))
            elif rating != "high" and blank((src.get("appraisal") or {}).get("concerns")):
                out.append(Issue("S06", sid, f"appraised {rating}; record the concerns that lowered it."))
    return out


def _evidence_rules(ledger: Ledger, cid: str, claim: dict, side: str) -> list[Issue]:
    out = []
    value = claim.get(side)
    if value is None:
        return out
    if not isinstance(value, list):
        return [Issue("E03", cid, f"'{side}' must be a list of evidence items.")]
    letter = "s" if side == "support" else "x"
    for n, item in enumerate(value, start=1):
        where = f"{cid}.{letter}{n}"
        if not isinstance(item, dict):
            out.append(Issue("E03", where, "is not an object with source, locator, kind and text."))
            continue
        sid = item.get("source")
        if sid not in ledger.sources:
            known = _allowed(sorted(ledger.sources)) or "none yet"
            out.append(Issue("E01", where, f"source {sid!r} is not in the ledger (known: {known})."))
        elif not ledger.is_included(sid):
            out.append(Issue("E02", where, f"{sid} is excluded."))
        missing = [f for f in ("locator", "text") if blank(item.get(f))]
        if missing:
            out.append(Issue("E03", where, f"missing {' and '.join(missing)}."))
        kind = item.get("kind")
        if kind not in EVIDENCE_KINDS:
            out.append(Issue("E03", where, f"kind is {kind!r}; expected one of: {_allowed(EVIDENCE_KINDS)}."))
        elif kind == "quote" and isinstance(item.get("text"), str) and len(item["text"]) > LONG_QUOTE:
            out.append(Issue("E07", where, f"quotation runs to {len(item['text'])} characters."))
        state = item.get("checked")
        if state is not None and state not in CHECK_STATES:
            out.append(Issue("V03", where, f"checked is {state!r}."))
        elif state == "mismatch":
            note = f" Note: {item['checked_note']}" if not blank(item.get("checked_note")) else ""
            out.append(Issue("V01", where, f"does not match {sid} at '{item.get('locator')}'.{note}"))
        if side == "contradicts" and ledger.is_included(sid) and blank(item.get("reconciled")):
            out.append(Issue("C03", where, f"how does {cid} account for this evidence from {sid}?"))
    return out


def claim_rules(ledger: Ledger) -> list[Issue]:
    out = []
    seen = set()
    for n, claim in enumerate(ledger.raw_claims, start=1):
        if not isinstance(claim, dict):
            out.append(Issue("S07", f"claims entry {n}", "is not an object."))
            continue
        cid = claim.get("id")
        if not isinstance(cid, str) or not CLAIM_ID.match(cid):
            out.append(Issue("S02", f"claims entry {n}", f"id {cid!r} should look like C1."))
            continue
        if cid in seen:
            out.append(Issue("S02", cid, "this id is used by more than one claim."))
            continue
        seen.add(cid)

        for name in ("statement", "type", "theme", "certainty", "rationale"):
            if blank(claim.get(name)):
                out.append(Issue("S07", cid, f"'{name}' is missing."))
        ctype, stated = claim.get("type"), claim.get("certainty")
        if not blank(ctype) and ctype not in CLAIM_TYPES:
            out.append(Issue("S07", cid, f"type '{ctype}' is not one of: {_allowed(CLAIM_TYPES)}."))
        if not blank(stated) and stated not in LEVELS:
            out.append(Issue("S07", cid, f"certainty '{stated}' is not one of: {_allowed(LEVELS)}."))

        out += _evidence_rules(ledger, cid, claim, "support")
        out += _evidence_rules(ledger, cid, claim, "contradicts")

        based_on = claim.get("based_on")
        if based_on is not None and not isinstance(based_on, list):
            out.append(Issue("E05", cid, "'based_on' must be a list of claim ids."))
        for ref in ledger.basis(claim):
            if ref == cid:
                out.append(Issue("E05", cid, "is based on itself."))
            elif ref not in ledger.claims:
                out.append(Issue("E05", cid, f"is based on {ref}, which does not exist."))

        support = ledger.usable(claim, "support")
        valid_basis = [b for b in ledger.basis(claim) if b in ledger.claims and b != cid]
        if ctype == "finding" and not support:
            out.append(Issue("E04", cid, "add evidence, or change the claim's type."))
        if ctype in DERIVED_TYPES and not support and not valid_basis:
            out.append(Issue("E05", cid, f"a {ctype} needs based_on or evidence of its own."))

        ceiling = claim_ceiling(ledger, claim)
        if ceiling is not None and stated in LEVELS and level(stated) > level(ceiling.level):
            code = "C02" if ctype in DERIVED_TYPES and valid_basis else "C01"
            out.append(Issue(code, cid, f"rated {stated}; ceiling is {ceiling.level} because "
                                        f"{'; '.join(ceiling.reasons)}."))
    return out


def coverage_rules(ledger: Ledger) -> list[Issue]:
    out = []
    included = ledger.included()
    for sid in sorted(set(included) - ledger.cited_sources()):
        out.append(Issue("E06", sid, "supports or contradicts no claim."))
    lineages = {s.get("lineage") for s in included.values() if not blank(s.get("lineage"))}
    if len(included) > 1 and len(lineages) == 1:
        out.append(Issue("E09", "ledger", f"all {len(included)} included sources share lineage {lineages.pop()}."))
    has_dissent = any(ledger.usable(c, "contradicts") for c in ledger.claims.values())
    if ledger.claims and len(included) >= DISSENT_EXPECTED_FROM and not has_dissent:
        out.append(Issue("E08", "ledger", f"{len(included)} included sources and no contradicting evidence on any claim."))
    return out


def verification_rules(ledger: Ledger) -> list[Issue]:
    pending = [r["address"] for r in required_checks(ledger) if r["item"].get("checked") != "confirmed"
               and r["item"].get("checked") != "mismatch"]
    if not pending:
        return []
    shown = ", ".join(pending[:8]) + (f" and {len(pending) - 8} more" if len(pending) > 8 else "")
    return [Issue("V02", "ledger", f"{len(pending)} item(s) to re-read at the source: {shown}.")]


def check_ledger(ledger: Ledger) -> list[Issue]:
    return (header_rules(ledger) + protocol_rules(ledger) + source_rules(ledger) + claim_rules(ledger)
            + coverage_rules(ledger) + verification_rules(ledger))
