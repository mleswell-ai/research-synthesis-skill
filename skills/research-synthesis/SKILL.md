---
name: research-synthesis
description: Synthesises evidence from multiple sources into a decision-ready, fully traceable report. Frames the question, weighs each source, records evidence in a claim-level ledger, builds claims across sources (thematic, narrative, framework, quantitative or mixed), computes how certain each claim is allowed to be, stress-tests the conclusions and verifies every citation. Use when asked for a research synthesis, evidence synthesis, literature review, systematic, scoping or rapid review, evidence summary or briefing, "what does the research say", the state of the evidence, or to combine, compare or reconcile papers, studies, reports, interview transcripts, survey responses or other research data. Also use to audit or strengthen an existing review. Not for summarising a single document or for quick factual lookups.
license: MIT
compatibility: Scripts need Python 3.9 or later (standard library only). Without code execution the method still applies; keep the ledger as tables and apply the rules by hand.
metadata:
  version: 1.0.0
---

# Research synthesis

A synthesis answers a question that no single source answers: what the body of evidence
supports, how sure anyone can be, where sources disagree and why, and what follows for
the decision in hand. A list of summaries is not a synthesis.

## The three questions

Every statement in the output must survive three questions. The whole method, and the
`ledger.py` tool, exist to make the answers checkable.

1. **Where exactly does this come from?** A named place in a source that was read.
   The answer is a **locator**.
2. **How many separate times was it observed?** Ten articles repeating one study are one
   observation. The answer is a count of **lineages**.
3. **How sure does that allow us to be?** The structure of the evidence sets a
   **ceiling** on certainty; judgement can only go lower.

## Rules that do not bend

- Cite only what was read. Record how it was read (`full-text`, `abstract-only`,
  `secondary-citation`); anything less than full text cannot carry a confident claim.
- No reference, author, year, figure or quotation comes from memory. If it cannot be
  found, it is not cited.
- Every figure and quotation has a locator, captured while reading.
- What sources report (**finding**), what it is taken to mean (**interpretation**) and
  what should be done (**recommendation**) are kept apart, and the last two can never be
  more certain than the findings beneath them.
- Evidence against a claim is recorded beside the evidence for it.
- "The evidence is insufficient" is a legitimate answer. Absence of evidence is not
  evidence of absence.

## Choose a mode

When unsure, take the lighter mode and say so.

| Mode | Use when | Sources | Search | Output |
| --- | --- | --- | --- | --- |
| **Rapid** | A bounded answer, mostly from supplied material | about 3 to 10 | None or light | A brief, often in chat ([assets/brief-template.md](assets/brief-template.md)) |
| **Standard** | A real decision rests on it | about 10 to 30 | Structured, logged | Full report ([assets/report-template.md](assets/report-template.md)) |
| **Systematic** | The method must be reproducible | As the protocol yields | Exhaustive, logged, counted | Full report, protocol and tables |

Two variations:

- **Primary qualitative data** (interviews, open survey responses, feedback, tickets):
  same workflow; read [references/qualitative-data.md](references/qualitative-data.md) first.
- **An existing synthesis to assess**: go to "Auditing someone else's synthesis" below.

## Workflow

Copy this into the working notes and tick as you go. The order matters: each step
produces what the next one needs, and skipping one produces a known failure
([references/failure-modes.md](references/failure-modes.md)).

```
- [ ] 1 Frame        question, decision, scope, criteria fixed before reading
- [ ] 2 Gather       ledger started; searches logged, or supplied corpus inventoried
- [ ] 3 Weigh        every source screened, appraised, given a lineage
- [ ] 4 Extract      evidence into the ledger with locators
- [ ] 5 Build        claims across sources; contradictions reconciled or marked unexplained
- [ ] 6 Rate         certainty at or below each ceiling, with a reason
- [ ] 7 Break        keystones examined, rival accounts tried, claims revised
- [ ] 8 Write        answer first, tied to the decision
- [ ] 9 Re-read      worksheet confirmed; `check` and `report` clean; rubric passed
```

### 1 Frame

Settle, in a line or two each: the **question** in a form that could be answered "no" or
"it depends"; the **decision** it serves and who uses it; the **scope** (population or
context, period, place, source types); and the **inclusion and exclusion criteria**.

Fix the criteria before reading. Criteria adjusted after seeing results are how a
synthesis comes to confirm what its author expected. If one must change, record the
change and the reason.

Ask the user at most two or three questions, only where the answer would change the work
(usually the decision, the scope boundary, the mode). If they would rather not answer,
proceed and list the assumptions at the top of the output.

Question frameworks, review types and a protocol outline:
[references/scoping-and-protocol.md](references/scoping-and-protocol.md).

### 2 Gather

Start the ledger. This also fixes today's date, which must not be assumed:

```bash
python scripts/ledger.py new ledger.json --question "..." --purpose "..." --mode standard --corpus searched
```

`--corpus` is `supplied`, `searched` or `mixed`. The ledger is one JSON file holding the
protocol, every source considered and every claim with its evidence. It is the working
memory of the synthesis: keep it on disk and current. Fields and a filled example:
[references/evidence-ledger.md](references/evidence-ledger.md) and
[examples/flexible-start/](examples/flexible-start/README.md).

**Supplied corpus**: give every item a source id (`S1`, `S2`, ...) and say in the report
that the synthesis covers only what was supplied.

**Searching**:

- Begin with short, broad queries to learn the field's vocabulary, then narrow.
- Log every query in the ledger: where, query, date, number of results.
- Go to the original. When an article reports a study, find and cite the study; if it
  cannot be obtained, cite the article and record `secondary-citation`.
- Search on purpose for null results, contrary findings and unpublished or grey
  material. Published evidence over-represents positive results.
- Follow reference lists backwards and citations forwards.
- Stop when new searches return mostly known sources, or the mode's budget is spent. Say
  which.

For large or separable jobs where subagents are available:
[references/parallel-research.md](references/parallel-research.md).

### 3 Weigh

Apply the criteria to each candidate. Excluded sources stay in the ledger with a reason.

For each included source record:

- an **appraisal** (`high`, `moderate`, `low`, `very-low`) with the specific concerns.
  Appraise fitness for this question, not prestige:
  [references/source-appraisal.md](references/source-appraisal.md);
- a **lineage** (`L1`, `L2`, ...). Sources share a lineage when they trace to one
  origin: a study and its preprint, press coverage and follow-up; several papers on one
  dataset; pages restating one report. Certainty depends on lineages, not citations.

### 4 Extract

For each source, record what bears on the question as evidence items: the source id, a
locator, the kind (`quote`, `paraphrase`, `data`) and the text. Include the population
and context, and anything that limits how far it travels. Paraphrase by default; quote
only the decisive words. Record what the source reports, not what would be convenient.

### 5 Build

Work across sources, never one source at a time.

1. **Pick the method** to fit the question and the evidence: thematic synthesis for
   qualitative or mixed evidence; narrative synthesis with a structured summary of
   effects for varied quantitative evidence; meta-analysis only when studies are alike
   enough for an average to mean something.
   [references/synthesis-methods.md](references/synthesis-methods.md)
2. **Group evidence by what it says**, not by source and not by shared vocabulary.
3. **Write each group as a claim**: a sentence that could be wrong. "Feedback timing" is
   a topic. "Delayed feedback outperformed immediate feedback on retention tasks but not
   on procedural ones" is a claim.
4. **Attach the evidence both ways**: items that support it, and items that contradict it.
5. **Reconcile each contradiction** in the item's `reconciled` field: a difference in
   population, measure, dose, time horizon, comparison, design quality or interest. If
   nothing explains it, write `unexplained`. Unreconciled contradictions lower the ceiling.
6. **Never tally significant against non-significant studies.** Report direction, size
   and range. Read [references/quantitative-evidence.md](references/quantitative-evidence.md)
   before reporting or comparing any effect.
7. **Count honestly**: "9 of 14 participants", "3 of 5 trials", not "most".

Have as many claims as the decision needs and no more. If a reader could not hold them
in mind, the grouping is not finished.

### 6 Rate

```bash
python scripts/ledger.py ceilings ledger.json
```

This prints, for each claim, the highest certainty its recorded evidence can carry and
the constraint that binds: one lineage, nothing sound read in full, an unreconciled
contradiction, or a weak claim underneath a recommendation.

Then judge. Set each claim's `certainty` **at or below** its ceiling, lowering for risk
of bias, inconsistency, indirectness, imprecision and probable missing evidence, and
give a one-sentence `rationale` naming what set it. Word claims to match:

| Certainty | Wording |
| --- | --- |
| High | "X increases Y" |
| Moderate | "X probably increases Y" |
| Low | "X may increase Y" |
| Very low | "It is unclear whether X increases Y" |

Rules, qualitative and non-research evidence, worked examples:
[references/certainty.md](references/certainty.md).

### 7 Break

Try to break the conclusions before a reader does.

```bash
python scripts/ledger.py keystones ledger.json
```

A **keystone** is a lineage a claim cannot stand without: remove it and the claim loses
its evidence or could no longer be rated as stated. Then, for each claim the bottom line
depends on:

- **Keystone**: re-read each keystone source in full. What else would be true if it is
  right, and is that seen anywhere?
- **Rival account**: write the best alternative explanation of the same evidence
  (chance, selection, confounding, measurement, reverse causation, an interested source).
  Name the observation that would separate the two, and look for it.
- **Reversal**: from the ledger alone, draft the bottom line that someone expecting the
  opposite would write. Wherever that draft is defensible, the claim is overstated.
- **Transfer**: does the evidence come from settings like the one the decision is about?
  If not, treat it as indirect and lower the rating.
- **Silence**: what evidence ought to exist if the claim were true, and was it searched for?

Put what this turns up into the ledger (new contradicting items, changed ratings,
narrower claims). Finding nothing is an acceptable outcome when it is true. Where
subagents exist, hand this step to a fresh reader given only the ledger.

### 8 Write

Answer first. The report has seven parts (rapid briefs may omit the method):

1. **Bottom line**: the answer in two to four sentences, in wording that carries its
   certainty.
2. **What this means for the decision**: interpretations and recommendations, labelled,
   including "do not act" and "the evidence cannot decide this" where honest, and what
   would change the conclusion.
3. **Findings**: one sub-heading per claim, written as the claim, with its id (`[C1]`),
   a `Certainty:` line with the reason, the evidence and citations (`[S3, S7]`), and for
   whom it holds.
4. **Where the evidence disagrees**, and why.
5. **Gaps and limitations**: of the evidence, and of this synthesis.
6. **How this was done**: question, criteria, search, counts, appraisal, method.
7. **Sources**: every cited source by id.

Be definite where the evidence allows and plain where it does not. Hedging every
sentence equally hides the difference between strong and weak findings, which is the
thing the reader most needs.

### 9 Re-read

```bash
python scripts/ledger.py worksheet ledger.json
```

The worksheet lists the evidence that must be read again at its locator: every figure,
every quotation and everything from a keystone. Open each source and compare. Then
record the result:

```bash
python scripts/ledger.py mark ledger.json confirmed C1.s1 C1.s2
python scripts/ledger.py mark ledger.json mismatch C2.s1 --note "Table 3 gives 0.03, not 0.30"
```

Correct any mismatch in the ledger and the report before confirming it. Marking an item
confirmed without re-reading it defeats the only check that catches a wrong citation.

Then run the checks, fix what they report and repeat until both are clean:

```bash
python scripts/ledger.py check ledger.json
python scripts/ledger.py report report.md ledger.json
```

`python scripts/ledger.py explain <CODE>` says why any rule exists. Outside rapid mode,
`report` fails while required evidence is unconfirmed. For an appendix,
`python scripts/ledger.py tables ledger.json` renders the evidence tables, and
`trace ledger.json C1` shows any claim's path back to its sources.

Last, score the draft against [references/quality-rubric.md](references/quality-rubric.md)
and fix anything below the pass mark.

## Updating a synthesis

When new evidence arrives, add the sources to the existing ledger, set `as_of` to the
new date, extract, and run `ceilings` and `keystones` again: a new lineage may raise a
ceiling, and a new contradiction may lower one. Note what changed under
`protocol.deviations`, and say in the report which conclusions moved and why.

## Auditing someone else's synthesis

1. Reconstruct its implied question, criteria and method.
2. Check its citations against the sources, starting with those its conclusions rest on.
   Do not assert what an unread source "really" says; report it as unchecked.
3. Score it with [references/quality-rubric.md](references/quality-rubric.md) and test it
   against [references/failure-modes.md](references/failure-modes.md).
4. Report the verdict first, then what holds, what is unsupported, and the specific
   changes that would fix it, in order of importance.

## Reference files

| File | Read when |
| --- | --- |
| [references/scoping-and-protocol.md](references/scoping-and-protocol.md) | Framing the question, choosing a review type, writing a protocol |
| [references/source-appraisal.md](references/source-appraisal.md) | Appraising a source or assigning lineages |
| [references/evidence-ledger.md](references/evidence-ledger.md) | Editing the ledger; a rule code needs explaining |
| [references/synthesis-methods.md](references/synthesis-methods.md) | Choosing and carrying out the synthesis method |
| [references/quantitative-evidence.md](references/quantitative-evidence.md) | Any effect size, statistic or pooled estimate appears |
| [references/qualitative-data.md](references/qualitative-data.md) | The material is interviews, open responses or feedback |
| [references/certainty.md](references/certainty.md) | Rating certainty; understanding a ceiling |
| [references/parallel-research.md](references/parallel-research.md) | Delegating parts of the work to subagents |
| [references/failure-modes.md](references/failure-modes.md) | Something looks off; auditing; final check |
| [references/quality-rubric.md](references/quality-rubric.md) | Scoring a draft or an existing synthesis |
| [examples/flexible-start/](examples/flexible-start/README.md) | Seeing a finished ledger and report |
