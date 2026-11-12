"""Human-readable views of a ledger: ceilings, keystones, the verification worksheet,
a claim's trace back to its sources, and Markdown tables for a report appendix."""

from __future__ import annotations

import re
from collections import Counter

from .ceiling import claim_ceiling, keystones, lineage_key, required_checks
from .schema import LEVELS, Ledger, blank, level

# Longer text is shortened in table cells so that tables stay readable.
CELL_WIDTH = 110


def cell(value) -> str:
    """A value made safe for one Markdown table cell (safe to apply twice)."""
    if value is None:
        return ""
    if isinstance(value, list):
        value = "; ".join(str(v) for v in value)
    return re.sub(r"(?<!\\)\|", r"\\|", " ".join(str(value).split()))


def clip(value, width: int = CELL_WIDTH) -> str:
    text = cell(value)
    return text if len(text) <= width else text[: width - 3].rstrip() + "..."


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    return "\n".join(lines + ["| " + " | ".join(r) + " |" for r in rows])


def ceilings_view(ledger: Ledger) -> str:
    if not ledger.claims:
        return "No claims in the ledger yet."
    lines = []
    for cid, claim in ledger.claims.items():
        ceiling = claim_ceiling(ledger, claim)
        stated = claim.get("certainty") or "(unrated)"
        if ceiling is None:
            lines.append(f"{cid}  stated {stated:9}  ceiling n/a       no usable evidence or basis")
            continue
        if stated in LEVELS and level(stated) > level(ceiling.level):
            verdict = "TOO HIGH"
        elif stated in LEVELS and level(stated) < level(ceiling.level):
            verdict = "below ceiling"
        else:
            verdict = "at ceiling" if stated in LEVELS else ""
        lines.append(f"{cid}  stated {stated:9}  ceiling {ceiling.level:9} {verdict}")
        for reason in ceiling.reasons or ["two or more sound lineages, or a sound review, and no unreconciled contradiction"]:
            lines.append(f"      - {reason}")
    lines.append("")
    lines.append("A ceiling is a limit, not a target. Rate below it for risk of bias, inconsistency,")
    lines.append("indirectness, imprecision or likely missing evidence (references/certainty.md).")
    return "\n".join(lines)


def keystones_view(ledger: Ledger) -> str:
    stones = keystones(ledger)
    if not stones:
        return ("No keystones: no claim's stated certainty depends on a single lineage.\n"
                "(Claims with no usable evidence are reported by `check`.)")
    by_source: dict[str, list[str]] = {}
    lines = ["Keystone lineages: remove one and the claim could not stand as rated.", ""]
    for cid, found in stones.items():
        for stone in found:
            lines.append(f"{cid}  {stone['lineage']} ({', '.join(stone['sources'])}): {stone['effect']}")
            for sid in stone["sources"]:
                by_source.setdefault(sid, []).append(cid)
    lines.append("")
    lines.append("Check these sources first, and hardest:")
    for sid, cids in sorted(by_source.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        title = clip(ledger.sources.get(sid, {}).get("title"), 70)
        lines.append(f"  {sid}  carries {', '.join(cids)}  {title}")
    return "\n".join(lines)


def worksheet_view(ledger: Ledger) -> str:
    required = required_checks(ledger)
    if not required:
        return "Nothing requires confirmation: no quotations, figures or keystone evidence recorded."
    done = sum(1 for r in required if r["item"].get("checked") == "confirmed")
    lines = [f"Verification worksheet: {done} of {len(required)} confirmed.",
             "Open each source at the locator. Does it say this, for this population and outcome?",
             "Then: python scripts/ledger.py mark <ledger> confirmed <address> ...   (or: mismatch <address> --note \"...\")",
             ""]
    for r in required:
        item = r["item"]
        state = {"confirmed": "[x]", "mismatch": "[!]"}.get(item.get("checked"), "[ ]")
        sid = item.get("source")
        side = "supports" if r["side"] == "support" else "contradicts"
        lines.append(f"{state} {r['address']:8} {sid} at {item.get('locator')}  ({r['why']}; {side} {r['claim']})")
        lines.append(f"             {clip(item.get('text'), 150)}")
    return "\n".join(lines)


def trace_view(ledger: Ledger, cid: str, depth: int = 0, seen=None) -> str:
    seen = seen or set()
    pad = "    " * depth
    if cid not in ledger.claims:
        return f"{pad}{cid}: no such claim. Claims: {', '.join(ledger.claims) or 'none'}"
    if cid in seen:
        return f"{pad}{cid}: (already shown above)"
    seen.add(cid)
    claim = ledger.claims[cid]
    ceiling = claim_ceiling(ledger, claim)
    lines = [f"{pad}{cid} [{claim.get('type')}] {claim.get('statement')}",
             f"{pad}  certainty: {claim.get('certainty')} (ceiling {ceiling.level if ceiling else 'n/a'}). "
             f"{claim.get('rationale') or ''}".rstrip()]
    if not blank(claim.get("conditions")):
        lines.append(f"{pad}  holds for: {claim['conditions']}")
    for side, label in (("support", "supported by"), ("contradicts", "contradicted by")):
        for item in ledger.items(claim, side):
            sid = item.get("source")
            src = ledger.sources.get(sid, {})
            state = item.get("checked") or "unchecked"
            lines.append(f"{pad}  {label} {sid} at {item.get('locator')} [{item.get('kind')}, {state}]")
            lines.append(f"{pad}      \"{clip(item.get('text'), 200)}\"")
            lines.append(f"{pad}      {clip(src.get('title'), 80)} ({src.get('year')}); lineage "
                         f"{lineage_key(ledger, sid) if sid in ledger.sources else '?'}; appraised "
                         f"{ledger.appraisal(sid)}; {src.get('access')}")
            if side == "contradicts":
                lines.append(f"{pad}      reconciled: {item.get('reconciled') or '(not yet)'}")
    if ledger.basis(claim):
        lines.append(f"{pad}  based on:")
    for parent in ledger.basis(claim):
        lines.append(trace_view(ledger, parent, depth + 1, seen))
    return "\n".join(lines)


def tables_view(ledger: Ledger) -> str:
    sources = list(ledger.sources.values())
    included = [s for s in sources if s.get("status") == "included"]
    excluded = [s for s in sources if s.get("status") == "excluded"]
    out = ["## Evidence tables",
           f"Question: {cell(ledger.data.get('question'))}  \nEvidence gathered to: "
           f"{cell(ledger.data.get('as_of'))}. Mode: {cell(ledger.mode)}."]

    flow = ledger.protocol.get("flow") if isinstance(ledger.protocol.get("flow"), dict) else {}
    rows = [[label, str(flow[key])] for key, label in (
        ("identified", "Records identified"), ("after_dedup", "After duplicates removed"),
        ("screened", "Screened"), ("full_text_assessed", "Full texts assessed")) if flow.get(key)]
    lineages = {s.get("lineage") for s in included if not blank(s.get("lineage"))}
    rows += [["Sources recorded", str(len(sources))], ["Excluded", str(len(excluded))],
             ["Included", str(len(included))],
             ["Included and read in full", str(sum(1 for s in included if s.get("access") == "full-text"))],
             ["Independent lineages", str(len(lineages))]]
    out.append("### Flow\n\n" + md_table(["Stage", "Count"], rows))

    reasons = Counter(cell(s.get("exclusion_reason")) or "No reason recorded" for s in excluded)
    if reasons:
        out.append("### Exclusions by reason\n\n" + md_table(
            ["Reason", "Count"], [[r, str(n)] for r, n in reasons.most_common()]))

    log = ledger.protocol.get("search_log")
    entries = [e for e in log if isinstance(e, dict) and not blank(e.get("query"))] if isinstance(log, list) else []
    if entries:
        out.append("### Search log\n\n" + md_table(
            ["Where", "Query", "Date", "Results"],
            [[cell(e.get("where")), cell(e.get("query")), cell(e.get("date")), cell(e.get("results"))] for e in entries]))

    if included:
        out.append("### Included sources\n\n" + md_table(
            ["ID", "Source", "Type and design", "Context", "Access", "Lineage", "Appraisal", "Concerns"],
            [[cell(s.get("id")),
              cell(f"{cell(s.get('authors'))} ({cell(s.get('year'))}). {cell(s.get('title'))}".lstrip(" .")),
              cell(" / ".join(str(x) for x in (s.get("type"), s.get("design")) if x)),
              clip(s.get("context")), cell(s.get("access")), cell(s.get("lineage")),
              cell(ledger.appraisal(s.get("id"))), clip((s.get("appraisal") or {}).get("concerns"))]
             for s in included]))
    if excluded:
        out.append("### Excluded sources\n\n" + md_table(
            ["ID", "Source", "Reason"],
            [[cell(s.get("id")), cell(f"{cell(s.get('title'))} ({cell(s.get('year'))})"),
              cell(s.get("exclusion_reason"))] for s in excluded]))

    if ledger.claims:
        rows = []
        for cid, claim in ledger.claims.items():
            support = list(dict.fromkeys(i["source"] for i in ledger.usable(claim, "support")))
            against = list(dict.fromkeys(i["source"] for i in ledger.usable(claim, "contradicts")))
            ceiling = claim_ceiling(ledger, claim)
            rows.append([cid, cell(claim.get("type")), clip(claim.get("statement")),
                         cell(", ".join(support) or ", ".join(ledger.basis(claim))),
                         str(len({lineage_key(ledger, s) for s in support})) if support else "",
                         cell(", ".join(against)), cell(claim.get("certainty")),
                         ceiling.level if ceiling else "", clip(claim.get("rationale"))])
        out.append("### Claims\n\n" + md_table(
            ["ID", "Type", "Statement", "Rests on", "Lineages", "Evidence against", "Certainty", "Ceiling", "Why"], rows))

        ids = [s.get("id") for s in included]
        rows = []
        for cid, claim in ledger.claims.items():
            support = {i["source"] for i in ledger.usable(claim, "support")}
            against = {i["source"] for i in ledger.usable(claim, "contradicts")}
            if support or against:
                rows.append([cid] + ["+/-" if s in support and s in against else "+" if s in support
                                     else "-" if s in against else "" for s in ids])
        if rows and ids:
            out.append("### Evidence matrix\n\n`+` supports, `-` contradicts, blank = no evidence extracted.\n\n"
                       + md_table(["Claim"] + [cell(i) for i in ids], rows))
    return "\n\n".join(out) + "\n"
