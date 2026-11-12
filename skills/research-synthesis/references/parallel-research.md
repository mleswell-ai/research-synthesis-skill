# Parallel research with subagents

Read this only when a tool for delegating work to subagents is available.

## Contents

- When to delegate
- Division of labour
- Briefing a worker
- Merging
- Trust, but check
- Reviewer brief

## When to delegate

Delegation multiplies cost. It pays when the work divides into parts that do not need
each other's context:

| Situation | Approach |
| --- | --- |
| Up to about 10 sources, one question | One agent, no delegation |
| 10 to 30 sources, or two to four separable sub-questions | Two to four workers |
| Larger corpus or many distinct strands | One worker per strand; batch sources per worker |
| Counter-review and citation checking | A fresh worker, whatever the size |

Do not delegate the synthesis itself. Grouping, weighing and concluding need the whole
picture in one place.

## Division of labour

- **Lead**: frames the question, writes the protocol, splits the work, merges the
  ledger, synthesises, rates certainty, writes.
- **Workers**: search and screen one strand, or read and extract a batch of sources.
  They return ledger entries, not prose.
- **Reviewer** (fresh context): challenges the claims, or checks citations against
  sources. Sees the ledger and draft only, not the lead's reasoning.

## Briefing a worker

A worker knows only what the brief says. Vague briefs produce duplicated searches and
gaps. Every brief contains:

```
OBJECTIVE
The overall question, and the specific sub-question or batch this worker owns.

SCOPE AND BOUNDARIES
Inclusion and exclusion criteria (verbatim from the protocol).
What is out of scope and belongs to another worker.
Stop condition (number of sources, or diminishing returns).

SOURCES AND TOOLS
Where to look, what to prefer (primary sources over secondary; original studies over
coverage of them), what to avoid.

RULES
- Read the source before recording anything from it. Record the access level honestly.
- Every evidence item needs a locator captured while reading.
- Never supply a reference, figure or quotation from memory.
- Record sources considered and excluded, with reasons.
- Record evidence against the expected answer as carefully as evidence for it.
- Log each search: where, query, date, results.

OUTPUT
Write a JSON file at <path> containing:
  "search_log": [...],
  "sources": [...],     (ledger source objects, IDs prefixed with this worker's letter)
  "evidence": [ {"source": "...", "locator": "...", "kind": "...", "text": "...",
                 "bears_on": "which part of the question", "direction": "for|against|neutral"} ],
  "observations": "anything the lead should know: gaps, doubts, leads not followed"
Return only the file path and a three-line summary.
```

Have workers write to files and return a path. Passing full findings back through
conversation loses detail and fills the lead's context.

Give each worker its own ID prefix (`SA1`, `SB1`) so that merged IDs do not collide;
renumber to `S1...` after merging if preferred.

## Merging

1. Combine the workers' sources. Deduplicate by DOI, URL and title.
2. Assign lineages across the whole set, since two workers may have found different
   reports of one study.
3. Combine search logs.
4. Build claims from the pooled evidence items. Workers supply evidence; the lead forms
   the claims.
5. Run `python scripts/ledger.py check ledger.json`.

## Trust, but check

Worker output is a report of what a source says, not the source. Before a claim that the
bottom line depends on goes into the report, the lead (or the reviewer) opens the original
and confirms the evidence item against its locator. The same applies to every number and
quotation, and to any conflict between workers.

When workers disagree, resolve it from the original sources. Do not settle it by which
view more workers reported: agreement among workers reading the same material is not
independent confirmation.

## Reviewer brief

```
You are reviewing a draft research synthesis. You have the evidence ledger and the draft
claims. For each claim:
1. Does the recorded evidence support the statement as worded, including its strength?
2. Run `ledger.py keystones`. For each keystone, is the source strong enough to bear that weight?
3. What is the strongest reason it could be wrong?
4. Is the certainty rating justified by the rationale given?
For citation checking: run `ledger.py worksheet`, open each source at the locator and
mark each item confirmed or mismatch (with a note saying what the source says instead).
Report problems only where they are supported. Finding none is an acceptable result.
```
