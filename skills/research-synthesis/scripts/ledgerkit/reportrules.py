"""Rules applied to a written report, read against its ledger."""

from __future__ import annotations

import re

from .ceiling import required_checks
from .issues import Issue
from .schema import LEVELS, Ledger, level

# What each required part of a report is called, and heading words that satisfy it.
PARTS = (
    ("bottom line", ("bottom line", "summary", "key message", "answer"), True),
    ("findings", ("finding",), True),
    ("gaps and limitations", ("limitation", "gap", "caveat"), True),
    ("how this was done", ("how this was done", "method", "approach"), False),  # optional in rapid mode
    ("sources", ("sources", "references"), True),
)

CITED_SOURCES = re.compile(r"\[(S[A-Z]?\d+(?:\s*[,;]\s*S[A-Z]?\d+)*)\]")
CITED_CLAIMS = re.compile(r"\[(C\d+(?:\s*[,;]\s*C\d+)*)\]")
RATING_LINE = re.compile(r"(?:certainty|confidence)\**\s*:\**\s*\**\s*(very[\s-]low|high|moderate|low)\b", re.I)
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")

LEFTOVERS = re.compile(
    r"\bTODO\b|\bTBD\b|\bXXX\b|\[citation needed\]|lorem ipsum|\[S\?\]|\[C#\]|YYYY-MM-DD|\[rating\]|\[n\]"
    # Bracketed prompts from the report templates; a following "(" would make it a link.
    r"|\[(?:Title:|Claim as|The evidence:|Reason\.|Answer in|One line)[^\]]*\]?(?!\()",
    re.I,
)

# Support asserted without naming it. Fine when the same sentence carries a citation.
UNNAMED_SUPPORT = re.compile(
    r"\b(?:studies|research|evidence|data|experts?|scientists|researchers|the literature)\s+"
    r"(?:consistently\s+|clearly\s+|generally\s+|widely\s+)?"
    r"(?:show|shows|suggest|suggests|indicate|indicates|demonstrate|demonstrates|agree|agrees|"
    r"confirm|confirms|prove|proves|has shown|have shown|has found|have found)\b"
    r"|\bit is (?:well[\s-])?(?:known|established|documented|accepted)\b"
    r"|\b(?:numerous|many|several|most|countless) (?:studies|papers|experts|researchers|sources)\b",
    re.I,
)

# Figures that need a source: percentages, effect sizes, sample sizes, intervals,
# "9 of 14" counts and p-values.
FIGURE = re.compile(
    r"\d+(?:\.\d+)?\s?%|\b[dgr]\s?=\s?-?\d|\bn\s?=\s?\d|\bCI\b|\b\d+\s+(?:of|out of)\s+\d+\b|\bp\s?[<=]\s?0?\.\d",
    re.I,
)


def _without_code(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def _ids(group: str) -> list[str]:
    return [p.strip() for p in re.split(r"[,;]", group) if p.strip()]


def _outline(text: str) -> list[dict]:
    sections, current = [], None
    for number, line in enumerate(text.splitlines(), start=1):
        match = HEADING.match(line)
        if match:
            current = {"depth": len(match.group(1)), "title": match.group(2), "lines": [], "line": number}
            sections.append(current)
        elif current is not None:
            current["lines"].append(line)
    for section in sections:
        section["body"] = "\n".join(section.pop("lines"))
    return sections


def _subtree(sections: list[dict], start: int) -> list[dict]:
    """A section together with the deeper sections beneath it."""
    span = [sections[start]]
    for section in sections[start + 1:]:
        if section["depth"] <= sections[start]["depth"]:
            break
        span.append(section)
    return span


def _locate(sections: list[dict], words) -> int:
    for n, section in enumerate(sections):
        if any(w in section["title"].lower() for w in words):
            return n
    return -1


def _paragraphs(body: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def _sentences(paragraph: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(\[*])", " ".join(paragraph.split())) if s]


def check_report(raw: str, ledger: Ledger) -> list[Issue]:
    out: list[Issue] = []
    text = _without_code(raw)
    sections = _outline(text)
    included = set(ledger.included())
    rapid = ledger.mode == "rapid"

    for name, words, always in PARTS:
        if _locate(sections, words) < 0 and (always or not rapid):
            out.append(Issue("R01", "report", f"no section for {name} (a heading containing "
                                              f"{' or '.join(repr(w) for w in words[:3])})."))

    cited = {sid for m in CITED_SOURCES.finditer(text) for sid in _ids(m.group(1))}
    if not cited:
        out.append(Issue("R04", "report", "no citations in the form [S1]."))
    for sid in sorted(cited):
        if sid not in ledger.sources:
            out.append(Issue("R02", f"[{sid}]", "not in the ledger."))
        elif sid not in included:
            out.append(Issue("R03", f"[{sid}]", "the ledger marks this source excluded."))
    claim_refs = {cid for m in CITED_CLAIMS.finditer(text) for cid in _ids(m.group(1))}
    for cid in sorted(claim_refs - set(ledger.claims)):
        out.append(Issue("R05", f"[{cid}]", "not in the ledger."))

    for number, line in enumerate(text.splitlines(), start=1):
        found = LEFTOVERS.search(line)
        if found:
            out.append(Issue("R06", f"line {number}", f"'{found.group(0)}'."))

    findings_at = _locate(sections, ("finding",))
    findings_body = ""
    if findings_at >= 0:
        span = _subtree(sections, findings_at)
        findings_body = "\n\n".join(s["body"] for s in span)
        blocks = [s for s in span[1:] if s["depth"] == span[0]["depth"] + 1]
        if not blocks:
            out.append(Issue("R07", "findings", "no sub-headings."))
        for block in blocks:
            where = f"line {block['line']} \"{block['title'][:50]}\""
            whole = "\n".join(s["title"] + "\n" + s["body"] for s in _subtree(sections, sections.index(block)))
            rating = RATING_LINE.search(whole)
            if not rating:
                out.append(Issue("R08", where, "add 'Certainty: <rating>. <reason>'."))
            if not CITED_SOURCES.search(whole):
                out.append(Issue("R09", where, "no [S#] citation in this finding."))
            linked = [c for m in CITED_CLAIMS.finditer(whole) for c in _ids(m.group(1)) if c in ledger.claims]
            if not linked:
                out.append(Issue("R11", where, "no claim id in this finding."))
            elif rating:
                said = re.sub(r"\s+", "-", rating.group(1).strip().lower())
                recorded = [ledger.claims[c].get("certainty") for c in linked if ledger.claims[c].get("certainty") in LEVELS]
                if len(linked) == 1 and recorded and said != recorded[0]:
                    out.append(Issue("R10", where, f"report says {said}; ledger rates {linked[0]} {recorded[0]}."))
                elif recorded and level(said) > max(level(r) for r in recorded):
                    out.append(Issue("R10", where, f"report says {said}, above every linked claim ({', '.join(linked)})."))

    for cid, claim in ledger.claims.items():
        if claim.get("type") == "finding" and cid not in claim_refs:
            out.append(Issue("R12", cid, "not referenced anywhere in the report."))
    for sid in sorted(included - cited):
        out.append(Issue("R13", sid, "never cited."))

    sources_at = _locate(sections, ("sources", "references"))
    source_sections = _subtree(sections, sources_at) if sources_at >= 0 else []
    if source_sections:
        listed = "\n".join(s["title"] + "\n" + s["body"] for s in source_sections)
        for sid in sorted(cited & included):
            if not re.search(rf"\b{re.escape(sid)}\b", listed):
                out.append(Issue("R14", sid, "cited in the text but absent from the source list."))

    for section in sections:
        if section in source_sections:
            continue
        for paragraph in _paragraphs(section["body"]):
            for sentence in _sentences(paragraph):
                phrase = UNNAMED_SUPPORT.search(sentence)
                if phrase and not CITED_SOURCES.search(sentence):
                    out.append(Issue("R15", f"\"{sentence[:70]}...\"", f"'{phrase.group(0)}' has no citation."))

    for paragraph in _paragraphs(findings_body):
        if RATING_LINE.match(paragraph.lstrip("*_ ")):
            continue
        figure = FIGURE.search(paragraph)
        if figure and not CITED_SOURCES.search(paragraph):
            flat = " ".join(paragraph.split())
            out.append(Issue("R16", f"\"{flat[:70]}...\"", f"'{figure.group(0)}' has no citation in its paragraph."))

    if not rapid:
        pending = [r["address"] for r in required_checks(ledger) if r["item"].get("checked") != "confirmed"]
        if pending:
            shown = ", ".join(pending[:8]) + (f" and {len(pending) - 8} more" if len(pending) > 8 else "")
            out.append(Issue("V04", "ledger", f"{len(pending)} required item(s) unconfirmed: {shown}. "
                                              "Run `ledger.py worksheet`."))
    return out
