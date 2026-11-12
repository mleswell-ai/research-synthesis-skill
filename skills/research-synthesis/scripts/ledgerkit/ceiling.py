"""Certainty ceilings, keystone lineages and the evidence that must be re-checked.

A ceiling is the highest certainty a claim's recorded evidence can carry. It is computed
from the structure of the evidence, not from how persuasive it reads:

  * Sound support is a source appraised moderate or better AND read in full.
  * No sound support                                   -> ceiling low
    (very-low when every supporting source is appraised very-low)
  * Sound support from one lineage, no sound review     -> ceiling moderate
  * Sound support from two or more lineages, or a sound
    systematic review or meta-analysis                  -> ceiling high
  * An unreconciled contradiction lowers the ceiling to moderate, or to low when the
    contradicting source is appraised at least as highly as the best supporting source.
  * A derived claim (interpretation, recommendation) can be no more certain than the
    weakest claim it is based on.

The ceiling is a limit, not a rating. Judgement about bias, inconsistency, indirectness
and imprecision routinely puts the stated certainty below it (references/certainty.md).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .schema import DERIVED_TYPES, LEVELS, REVIEW_TYPES, Ledger, blank, level, weaker

UNEXPLAINED = re.compile(r"^\s*unexplained\b", re.I)


@dataclass
class Ceiling:
    level: str
    reasons: list[str] = field(default_factory=list)

    def lower_to(self, new_level: str, reason: str) -> None:
        if level(new_level) < level(self.level):
            self.level = new_level
        self.reasons.append(reason)


def lineage_key(ledger: Ledger, sid: str) -> str:
    """A source's lineage; a source with none recorded stands alone."""
    return ledger.lineage(sid) or f"({sid} alone)"


def unreconciled(item: dict) -> bool:
    text = item.get("reconciled")
    return blank(text) or bool(UNEXPLAINED.match(str(text)))


def evidence_ceiling(ledger: Ledger, claim: dict, without: str = ""):
    """Ceiling from a claim's own evidence, optionally ignoring one lineage.
    Returns None when no usable support remains."""
    sids = []
    for item in ledger.usable(claim, "support"):
        sid = item["source"]
        if sid not in sids and lineage_key(ledger, sid) != without:
            sids.append(sid)
    if not sids:
        return None

    best = max(level(ledger.appraisal(s)) for s in sids)
    sound = [s for s in sids if level(ledger.appraisal(s)) >= level("moderate") and ledger.read_in_full(s)]
    sound_lineages = sorted({lineage_key(ledger, s) for s in sound})
    sound_review = any(ledger.sources[s].get("type") in REVIEW_TYPES for s in sound)

    ceiling = Ceiling("high")
    if not sound:
        if best <= level("very-low"):
            ceiling.lower_to("very-low", "every supporting source is appraised very-low")
        else:
            ceiling.lower_to("low", "no supporting source is both appraised moderate or better and read in full")
    elif len(sound_lineages) < 2 and not sound_review:
        ceiling.lower_to("moderate", f"sound support comes from one lineage ({sound_lineages[0]}); high needs a "
                                     "second independent lineage or a sound systematic review")

    for item in ledger.usable(claim, "contradicts"):
        if not unreconciled(item):
            continue
        sid = item["source"]
        if level(ledger.appraisal(sid)) >= best:
            ceiling.lower_to("low", f"unreconciled contradiction from {sid}, appraised at least as highly as "
                                    "the best supporting source")
        else:
            ceiling.lower_to("moderate", f"unreconciled contradiction from {sid}")
    return ceiling


def claim_ceiling(ledger: Ledger, claim: dict):
    """Ceiling for any claim. None when there is nothing to compute it from."""
    own = evidence_ceiling(ledger, claim)
    if claim.get("type") not in DERIVED_TYPES:
        return own
    parents = [(b, ledger.claims[b].get("certainty")) for b in ledger.basis(claim)
               if b in ledger.claims and b != claim.get("id") and level(ledger.claims[b].get("certainty")) >= 0]
    if not parents:
        return own
    weakest = min(parents, key=lambda p: level(p[1]))
    ceiling = Ceiling(weakest[1], [f"rests on {weakest[0]}, rated {weakest[1]}"])
    if own is not None and level(own.level) < level(ceiling.level):
        ceiling = Ceiling(own.level, ceiling.reasons + own.reasons)
    return ceiling


def keystones(ledger: Ledger) -> dict[str, list[dict]]:
    """For each claim, the lineages its stated certainty depends on: remove one and the
    claim either loses all support or could no longer be rated as stated."""
    result: dict[str, list[dict]] = {}
    for cid, claim in ledger.claims.items():
        stated = claim.get("certainty")
        if stated not in LEVELS:
            continue
        support = ledger.usable(claim, "support")
        keys = []
        for item in support:
            key = lineage_key(ledger, item["source"])
            if key not in keys:
                keys.append(key)
        found = []
        for key in keys:
            remaining = evidence_ceiling(ledger, claim, without=key)
            sids = sorted({i["source"] for i in support if lineage_key(ledger, i["source"]) == key})
            if remaining is None:
                found.append({"lineage": key, "sources": sids, "effect": "sole support: without it the claim has no evidence"})
            elif level(remaining.level) < level(stated):
                found.append({"lineage": key, "sources": sids,
                              "effect": f"without it the ceiling falls to {remaining.level}, below the stated {stated}"})
        if found:
            result[cid] = found
    return result


def required_checks(ledger: Ledger) -> list[dict]:
    """Evidence that must be re-read at its locator before a report is final: every
    quotation and figure, and everything from a keystone lineage. Keystone items first."""
    stones = keystones(ledger)
    required = []
    for address, (claim, item, side) in ledger.address_book().items():
        sid = item.get("source")
        if not ledger.is_included(sid):
            continue
        cid = claim.get("id")
        key_lineages = {k["lineage"] for k in stones.get(cid, [])}
        is_keystone = side == "support" and lineage_key(ledger, sid) in key_lineages
        exact = item.get("kind") in ("quote", "data")
        if is_keystone or exact:
            why = "keystone" if is_keystone else str(item.get("kind"))
            if is_keystone and exact:
                why = f"keystone, {item.get('kind')}"
            required.append({"address": address, "claim": cid, "side": side, "item": item,
                             "why": why, "keystone": is_keystone})
    required.sort(key=lambda r: (not r["keystone"],))
    return required
