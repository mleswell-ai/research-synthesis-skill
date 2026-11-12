# Worked example: flexible start times

A complete run of the skill on the fictitious documents in
`evals/files/flexible-start/` in the repository, which were written
with traps in them: press coverage that double-counts a study, a source available only
as an abstract, a vendor case study, and an independent evaluation that cuts against the
headline result.

| File | What it is |
| --- | --- |
| `ledger.json` | The evidence ledger: 5 sources considered, 4 included, 6 claims |
| `report.md` | The report written from it |
| `tables.md` | Appendix tables from `ledger.py tables` |

It is also the reference answer for scenario 1 in `evals/evals.json`, so do not show it
to a session you are evaluating.

To see what the tool reports:

```bash
# run from the skill folder
python scripts/ledger.py ceilings  examples/flexible-start/ledger.json
python scripts/ledger.py keystones examples/flexible-start/ledger.json
python scripts/ledger.py trace     examples/flexible-start/ledger.json C2
python scripts/ledger.py report    examples/flexible-start/report.md examples/flexible-start/ledger.json
```

Things worth noticing:

- **C1** has two sound lineages, so its ceiling is high, yet it is rated low: both
  intervals reach zero and each study has a design weakness. The ceiling is a limit, and
  judgement does the rest.
- **C3** records a contradiction as `unexplained`, which caps it at low.
- **C4** rests on an abstract, so it cannot be rated above low whatever the abstract says.
- **S2**, the press article, is excluded with a reason and never counted.
- **C6**, the recommendation, cannot be rated above the findings it rests on.
