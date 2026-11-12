#!/usr/bin/env python3
"""Work with a research-synthesis evidence ledger.

    python scripts/ledger.py new ledger.json --question "..."   start a ledger dated today
    python scripts/ledger.py check ledger.json                  structure, links, ceilings
    python scripts/ledger.py ceilings ledger.json               how certain each claim may be, and why
    python scripts/ledger.py keystones ledger.json              which sources the conclusions depend on
    python scripts/ledger.py worksheet ledger.json              what to re-read at the source
    python scripts/ledger.py mark ledger.json confirmed C1.s1   record the result of re-reading
    python scripts/ledger.py trace ledger.json C1               a claim back to its sources
    python scripts/ledger.py tables ledger.json                 Markdown tables for an appendix
    python scripts/ledger.py report report.md ledger.json       check a written report
    python scripts/ledger.py explain C01                        why a rule exists

Exit status: 0 clean, 1 problems found, 2 a file could not be read or written.
Standard library only; Python 3.9 or later.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ledgerkit import __version__  # noqa: E402
from ledgerkit.issues import CATALOGUE, Issue, catalogue_table, errors, warnings  # noqa: E402
from ledgerkit.ledgerrules import check_ledger  # noqa: E402
from ledgerkit.render import ceilings_view, keystones_view, tables_view, trace_view, worksheet_view  # noqa: E402
from ledgerkit.reportrules import check_report  # noqa: E402
from ledgerkit.schema import CHECK_STATES, CORPORA, MODES, Ledger, LedgerUnreadable  # noqa: E402

CLEAN, PROBLEMS, UNREADABLE = 0, 1, 2

# Seconds to wait for a reference to respond before giving up on it. Slow publisher
# sites are common; a timeout is reported as "could not reach", never as a bad reference.
URL_TIMEOUT = 15


def conclude(issues: list[Issue], strict: bool, as_json: bool, subject: str, clean_note: str) -> int:
    failed = bool(errors(issues)) or (strict and bool(warnings(issues)))
    if as_json:
        print(json.dumps({"ok": not failed, "errors": len(errors(issues)), "warnings": len(warnings(issues)),
                          "issues": [i.as_dict() for i in issues]}, indent=2))
        return PROBLEMS if failed else CLEAN
    for issue in errors(issues) + warnings(issues):
        print(issue.line())
    if issues:
        print()
    print(f"{subject}: {len(errors(issues))} error(s), {len(warnings(issues))} warning(s).")
    if failed:
        print("Fix and run again. `python scripts/ledger.py explain <CODE>` says why a rule exists.")
        return PROBLEMS
    print(clean_note)
    return CLEAN


def url_notes(ledger: Ledger) -> list[str]:
    """Try each included source's DOI or URL. A reference that resolves exists; that is
    all this shows. It does not show the reference is the right work or says what is claimed."""
    import re
    import urllib.error
    import urllib.request

    notes = []
    for sid, src in sorted(ledger.included().items()):
        ref = str(src.get("ref") or "").strip()
        if ref.lower().startswith("doi:"):
            ref = "https://doi.org/" + ref[4:].strip()
        elif re.match(r"^10\.\d{4,9}/\S+$", ref):
            ref = "https://doi.org/" + ref
        if not ref.lower().startswith(("http://", "https://")):
            continue
        request = urllib.request.Request(ref, headers={"User-Agent": "research-synthesis-ledger"})
        try:
            with urllib.request.urlopen(request, timeout=URL_TIMEOUT):
                notes.append(f"resolves      {sid}  {ref}")
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 405, 429):  # sites that refuse scripts but serve readers
                notes.append(f"unconfirmed   {sid}  HTTP {exc.code}, open by hand: {ref}")
            else:
                notes.append(f"NOT FOUND     {sid}  HTTP {exc.code}: {ref}")
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            notes.append(f"unreachable   {sid}  {ref} ({exc})")
    return notes


def cmd_new(args) -> int:
    path = Path(args.ledger)
    if path.exists():
        print(f"'{path}' already exists; not overwriting it.")
        return UNREADABLE
    today = datetime.date.today().isoformat()
    data = {
        "question": args.question,
        "purpose": args.purpose or "",
        "as_of": today,
        "mode": args.mode,
        "protocol": {
            "corpus": args.corpus, "inclusion": [], "exclusion": [],
            "search_log": [], "synthesis_method": "", "assumptions": [], "deviations": [],
        },
        "sources": [],
        "claims": [],
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"Cannot write '{path}': {exc}.")
        return UNREADABLE
    print(f"Started {path} (as_of {today}, mode {args.mode}, corpus {args.corpus}).")
    print("Next: set the criteria in protocol, then add sources as you consider them. "
          "Field guide: references/evidence-ledger.md")
    return CLEAN


def cmd_check(args) -> int:
    ledger = Ledger.read(args.ledger)
    issues = check_ledger(ledger)
    if args.urls and not args.json:
        for note in url_notes(ledger):
            print(note)
        print()
    included = len(ledger.included())
    subject = f"{len(ledger.sources)} source(s) ({included} included), {len(ledger.claims)} claim(s)"
    return conclude(issues, args.strict, args.json, subject,
                    "Ledger holds together." + (" Review the warnings." if issues else ""))


def cmd_report(args) -> int:
    try:
        raw = Path(args.report).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Cannot read report '{args.report}': {exc}.")
        return UNREADABLE
    if not raw.strip():
        print(f"Report '{args.report}' is empty.")
        return UNREADABLE
    ledger = Ledger.read(args.ledger)
    ledger_errors = errors(check_ledger(ledger))
    if ledger_errors and not args.json:
        print(f"Note: the ledger itself has {len(ledger_errors)} error(s); run `check` and fix those first.\n")
    issues = check_report(raw, ledger)
    return conclude(issues, args.strict, args.json, "Report",
                    "Report agrees with the ledger." + (" Review the warnings." if issues else "")
                    + "\nNo script can tell whether a source says what is claimed: that is what the worksheet is for.")


def cmd_mark(args) -> int:
    ledger = Ledger.read(args.ledger)
    book = ledger.address_book()
    unknown = [a for a in args.addresses if a not in book]
    if unknown:
        print(f"No such evidence item: {', '.join(unknown)}. Addresses look like C1.s1 (support) or "
              f"C1.x1 (contradicting); `worksheet` lists them.")
        return UNREADABLE
    if args.state == "mismatch" and not args.note:
        print("A mismatch needs --note saying what the source says instead.")
        return UNREADABLE
    for address in args.addresses:
        _, item, _ = book[address]
        item["checked"] = args.state
        if args.note:
            item["checked_note"] = args.note
        elif "checked_note" in item:
            del item["checked_note"]
    try:
        ledger.write()
    except OSError as exc:
        print(f"Cannot write '{args.ledger}': {exc}.")
        return UNREADABLE
    print(f"Marked {len(args.addresses)} item(s) {args.state}.")
    if args.state == "mismatch":
        print("Now correct the evidence item (and the claim if it changes), then mark it confirmed.")
    return CLEAN


def cmd_view(args) -> int:
    ledger = Ledger.read(args.ledger)
    if args.command == "ceilings":
        text = ceilings_view(ledger)
    elif args.command == "keystones":
        text = keystones_view(ledger)
    elif args.command == "worksheet":
        text = worksheet_view(ledger)
    elif args.command == "trace":
        text = "\n\n".join(trace_view(ledger, cid) for cid in (args.claims or list(ledger.claims))) \
            or "No claims in the ledger yet."
    else:
        text = tables_view(ledger)
    output = getattr(args, "output", None)
    if output:
        try:
            Path(output).write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Cannot write '{output}': {exc}.")
            return UNREADABLE
        print(f"Wrote {output}")
    else:
        print(text, end="" if text.endswith("\n") else "\n")
    return CLEAN


def cmd_explain(args) -> int:
    if args.code is None:
        print(catalogue_table())
        return CLEAN
    code = args.code.upper()
    if code not in CATALOGUE:
        print(f"No rule '{args.code}'. Run `python scripts/ledger.py explain` for the full list.")
        return UNREADABLE
    severity, title, why = CATALOGUE[code]
    print(f"{code} ({severity}): {title}\n{why}")
    return CLEAN


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger.py", description="Work with a research-synthesis evidence ledger.")
    parser.add_argument("--version", action="version", version=f"ledgerkit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    p = sub.add_parser("new", help="start a ledger dated today")
    p.add_argument("ledger")
    p.add_argument("--question", required=True)
    p.add_argument("--purpose", help="the decision or use the synthesis serves")
    p.add_argument("--mode", choices=MODES, default="standard")
    p.add_argument("--corpus", choices=CORPORA, default="searched")
    p.set_defaults(run=cmd_new)

    p = sub.add_parser("check", help="check structure, evidence links, ceilings and verification state")
    p.add_argument("ledger")
    p.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    p.add_argument("--urls", action="store_true", help="also try each included source's DOI or URL (needs network)")
    p.add_argument("--json", action="store_true", help="print machine-readable results")
    p.set_defaults(run=cmd_check)

    for name, summary in (("ceilings", "show how certain each claim may be, and what limits it"),
                          ("keystones", "show which lineages each claim's rating depends on"),
                          ("worksheet", "list the evidence to re-read at the source")):
        p = sub.add_parser(name, help=summary)
        p.add_argument("ledger")
        p.set_defaults(run=cmd_view)

    p = sub.add_parser("mark", help="record the result of re-reading evidence at its source")
    p.add_argument("ledger")
    p.add_argument("state", choices=CHECK_STATES)
    p.add_argument("addresses", nargs="+", metavar="address", help="for example C1.s1 C2.x1")
    p.add_argument("--note", help="what the source says instead (required for mismatch)")
    p.set_defaults(run=cmd_mark)

    p = sub.add_parser("trace", help="follow claims back to their sources")
    p.add_argument("ledger")
    p.add_argument("claims", nargs="*", metavar="claim", help="claim ids; all claims when omitted")
    p.set_defaults(run=cmd_view)

    p = sub.add_parser("tables", help="render Markdown evidence tables")
    p.add_argument("ledger")
    p.add_argument("-o", "--output", help="write to this file")
    p.set_defaults(run=cmd_view)

    p = sub.add_parser("report", help="check a written report against its ledger")
    p.add_argument("report")
    p.add_argument("ledger")
    p.add_argument("--strict", action="store_true", help="fail on warnings as well as errors")
    p.add_argument("--json", action="store_true", help="print machine-readable results")
    p.set_defaults(run=cmd_report)

    p = sub.add_parser("explain", help="say why a rule exists; with no code, list every rule")
    p.add_argument("code", nargs="?")
    p.set_defaults(run=cmd_explain)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except LedgerUnreadable as exc:
        print(exc)
        return UNREADABLE


if __name__ == "__main__":
    sys.exit(main())
