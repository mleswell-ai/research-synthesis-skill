# The evidence ledger

## Contents

- What it is for
- Shape of the file
- Sources
- Claims and evidence items
- Addresses
- The `ledger.py` commands
- Rule codes
- Working habits

## What it is for

One JSON file holding the protocol, every source considered and every claim with the
exact evidence for and against it. Nothing reaches the report except through it, so that:

- no statement depends on recollection of what a source said;
- the work survives a long session, a hand-off or an update months later;
- the tool can compute what each claim's evidence is able to support;
- a reader can follow any sentence back to a page.

A finished example is in `examples/flexible-start/ledger.json`.

## Shape of the file

```json
{
  "question": "...",
  "purpose": "the decision this serves",
  "as_of": "2025-01-15",
  "mode": "rapid | standard | systematic",
  "protocol": {
    "corpus": "supplied | searched | mixed",
    "inclusion": ["..."],
    "exclusion": ["..."],
    "search_log": [{"where": "...", "query": "...", "date": "2025-01-15", "results": 42}],
    "flow": {"identified": 0, "after_dedup": 0, "screened": 0, "full_text_assessed": 0},
    "synthesis_method": "...",
    "assumptions": ["made without the user's confirmation"],
    "deviations": ["changes to the plan, with reasons"]
  },
  "sources": [],
  "claims": []
}
```

`python scripts/ledger.py new` writes this skeleton with today's date. `inclusion` and a
`search_log` are required in systematic mode with a searched corpus; a search log is
expected whenever the corpus was searched.

## Sources

```json
{
  "id": "S1",
  "title": "As printed on the source",
  "authors": "optional",
  "year": 2022,
  "ref": "DOI, URL or file path",
  "type": "primary-study",
  "design": "RCT",
  "access": "full-text",
  "status": "included",
  "lineage": "L1",
  "appraisal": {"rating": "moderate", "concerns": ["18% attrition", "developer-led"]},
  "context": "58 schools, 3,100 pupils, one school year"
}
```

| Field | Values and notes |
| --- | --- |
| `id` | `S1`, `S2`, ... A worker letter is allowed when merging parallel work: `SA1` |
| `year` | A year, or `"n.d."` |
| `type` | `systematic-review`, `meta-analysis`, `primary-study`, `report`, `dataset`, `grey-literature`, `news`, `expert-opinion`, `primary-data`, `internal` |
| `access` | `full-text`, `abstract-only`, `secondary-citation` |
| `status` | `included`, or `excluded` with an `exclusion_reason` |
| `lineage` | Required when included. Sources tracing to one origin share a value |
| `appraisal.rating` | Required when included: `high`, `moderate`, `low`, `very-low`, with `concerns` unless high |

Use `primary-data` for the user's own material; each participant or dataset is a source.
Add a source when it is first considered, not when it is first cited.

## Claims and evidence items

```json
{
  "id": "C1",
  "statement": "A full sentence that could be wrong.",
  "type": "finding",
  "theme": "Short label",
  "support": [
    {"source": "S1", "locator": "Table 4, p. 31", "kind": "data",
     "text": "Effect size 0.12 (95% CI 0.02 to 0.22) on the comprehension test at one year"}
  ],
  "contradicts": [
    {"source": "S5", "locator": "Summary, p. 1", "kind": "paraphrase",
     "text": "District scores did not change after adoption",
     "reconciled": "Before-and-after design with no comparison group."}
  ],
  "certainty": "moderate",
  "rationale": "Two trials agree; lowered because the larger effect is developer-led.",
  "conditions": "Pupils aged 7 to 11"
}
```

| Field | Notes |
| --- | --- |
| `type` | `finding` (what sources report), `interpretation` (what it is taken to mean) or `recommendation` (what to do) |
| `support` | Evidence items for the claim. Required for a finding |
| `contradicts` | Evidence items against it |
| `based_on` | For interpretations and recommendations: the claim ids they follow from |
| `certainty` | `high`, `moderate`, `low`, `very-low`; never above the ceiling |
| `rationale` | One sentence naming what set the rating |
| `conditions` | For whom, where or when the claim holds |

Evidence item fields:

| Field | Notes |
| --- | --- |
| `source` | An included source id |
| `locator` | Page, section, table, figure, paragraph, timestamp or line range |
| `kind` | `quote` (exact words), `paraphrase`, or `data` (a figure with units, comparison and time point) |
| `text` | Written so it makes sense without the source to hand |
| `reconciled` | On contradicting items: how the claim accounts for this evidence, or `unexplained` |
| `checked` | Set by `ledger.py mark`: `confirmed` or `mismatch` (with `checked_note`) |

## Addresses

Each evidence item has an address: `C1.s2` is the second supporting item of C1, `C1.x1`
its first contradicting item. The worksheet, `mark` and error messages use them.

## The `ledger.py` commands

Run from the skill folder as `python scripts/ledger.py <command>`.

| Command | Purpose |
| --- | --- |
| `new LEDGER --question "..." [--purpose --mode --corpus]` | Start a ledger dated today |
| `check LEDGER [--strict] [--urls] [--json]` | Apply every ledger rule. `--urls` also tries each DOI or URL |
| `ceilings LEDGER` | The highest certainty each claim's evidence allows, and the binding constraint |
| `keystones LEDGER` | The lineages each claim's rating depends on, and which sources to scrutinise first |
| `worksheet LEDGER` | The evidence that must be re-read at its locator, keystones first |
| `mark LEDGER confirmed\|mismatch ADDRESS... [--note]` | Record the result of re-reading |
| `trace LEDGER [CLAIM...]` | A claim's path to its evidence and sources |
| `tables LEDGER [-o FILE]` | Markdown tables: flow, sources, claims, evidence matrix |
| `report REPORT LEDGER [--strict] [--json]` | Check a written report against the ledger |
| `explain [CODE]` | Why a rule exists; with no code, the full list |

Exit status is 0 when clean, 1 when problems were found, 2 when a file could not be read.
A resolving DOI or URL shows that something exists at the address, nothing more.

## Rule codes

Errors must be fixed. Warnings should be fixed or answered in the report.

| Code | Severity | Rule |
| --- | --- | --- |
| S01 | error | Ledger header incomplete |
| S02 | error | Identifier malformed or repeated |
| S03 | error | Source record incomplete |
| S04 | error | Excluded source has no reason |
| S05 | error | Included source has no lineage or appraisal |
| S06 | warning | Appraisal lowered without stated concerns |
| S07 | error | Claim record incomplete |
| P01 | error | Corpus not declared |
| P02 | error | Systematic mode without inclusion criteria |
| P03 | error | Systematic mode without a search log |
| P04 | warning | Searched corpus without a search log |
| P05 | warning | Search log entry incomplete |
| E01 | error | Evidence cites an unknown source |
| E02 | error | Evidence cites an excluded source |
| E03 | error | Evidence item incomplete |
| E04 | error | Finding has no usable support |
| E05 | error | Derived claim has no valid basis |
| E06 | warning | Included source is unused |
| E07 | warning | Quotation is long |
| E08 | warning | No contrary evidence recorded anywhere |
| E09 | warning | Whole synthesis rests on one lineage |
| C01 | error | Certainty exceeds what the evidence can carry |
| C02 | error | Derived claim is more certain than its basis |
| C03 | warning | Contradiction not reconciled |
| V01 | error | Evidence failed its check against the source |
| V02 | warning | Evidence awaiting confirmation |
| V03 | error | Unknown check state |
| V04 | error | Report finalised with unconfirmed evidence |
| R01 | error | Report section missing |
| R02 | error | Report cites a source that is not in the ledger |
| R03 | error | Report cites an excluded source |
| R04 | error | Report has no citations |
| R05 | error | Report refers to an unknown claim |
| R06 | error | Placeholder or template text remains |
| R07 | error | Findings are not separated |
| R08 | error | Finding has no certainty rating |
| R09 | error | Finding has no citation |
| R10 | error | Report and ledger disagree on certainty |
| R11 | warning | Finding not linked to a ledger claim |
| R12 | warning | Ledger finding missing from the report |
| R13 | warning | Included source never cited in the report |
| R14 | warning | Cited source missing from the source list |
| R15 | warning | Claim of support with no source |
| R16 | warning | Figure with no source |

## Working habits

- Capture the locator at the moment of reading. Locators rebuilt afterwards are where
  wrong citations come from.
- When a claim is reworded in the report, reword it in the ledger. The two must agree.
- When contrary evidence turns up, add it under `contradicts` at once, then look at the
  ceiling again.
- Never mark an item `confirmed` without reopening the source.
