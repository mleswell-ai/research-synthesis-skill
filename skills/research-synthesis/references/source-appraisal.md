# Source appraisal

## Contents

- What appraisal is for
- Universal questions
- Appraisal by design
- Non-academic sources
- Lineages
- Access levels
- Assigning the rating
- Field-specific rating schemes

## What appraisal is for

Appraisal decides how much weight a source can bear for this question. It is not a
judgement of the authors or the venue. A well-run study can be weak evidence for a
question it was not designed to answer, and a prestigious journal publishes flawed work.

Record, for each included source, a rating and the specific concerns behind it. "Low:
self-selected sample of 40, no comparison group, outcomes self-reported" is useful.
"Low quality" is not.

## Universal questions

Ask these of any source:

1. **Access**: was the source in a position to know? First-hand data, or a report of
   someone else's?
2. **Method**: is it clear how the information was produced, and is that method capable
   of supporting the claim made?
3. **Sample**: who or what was studied, how many, how selected, and how many were lost?
4. **Comparison**: compared with what? Could the comparison groups differ in other ways?
5. **Measurement**: are the outcomes measured validly, and by someone who did not know
   which group was which?
6. **Analysis**: are the conclusions those the data support? Were outcomes or analyses
   chosen after seeing the results?
7. **Interest**: who funded or produced it, and what do they gain from a given answer?
8. **Directness**: how closely do the population, intervention, setting and outcome match
   the question in hand?
9. **Currency**: could the finding have been overtaken by later evidence or events?
10. **Corroboration**: has anyone independent found the same?

## Appraisal by design

Use the established tool for the design where rigour matters (Systematic mode); use its
core questions informally in Rapid and Standard modes.

| Design | Established tools | Core questions |
| --- | --- | --- |
| Systematic review or meta-analysis | AMSTAR 2, ROBIS | Pre-registered protocol? Comprehensive search? Included studies appraised? Appropriate pooling? Publication bias considered? |
| Randomised trial | Cochrane RoB 2 | Randomisation and concealment sound? Deviations from intended intervention? Missing outcome data? Blinded outcome measurement? Selective reporting? |
| Non-randomised intervention study | ROBINS-I | Confounding controlled? Selection into groups? Classification of intervention? Missing data? |
| Cohort or case-control study | Newcastle-Ottawa Scale, JBI checklists | Groups comparable? Exposure and outcome ascertained reliably? Follow-up adequate? |
| Cross-sectional survey | JBI checklist | Sampling frame and response rate? Validated instrument? Claims limited to association? |
| Qualitative study | CASP qualitative checklist | Clear aim and suitable design? Recruitment and data collection described? Researcher's role considered? Analysis rigorous and findings supported by data? |
| Mixed methods | MMAT | Each strand sound? Integration justified? |
| Case study | JBI checklist | Case selection explained? Enough context to judge transfer? |

A systematic review is only as good as its included studies and its own conduct. Do not
rate a review high because it is a review.

## Non-academic sources

Much useful evidence is not peer-reviewed: government and regulator reports, official
statistics, evaluations, industry research, technical documentation, journalism, expert
commentary. Appraise it with the AACODS headings:

- **Authority**: who produced it, and are they credible on this subject?
- **Accuracy**: is the method stated, are sources given, can the figures be checked?
- **Coverage**: what limits apply (place, period, population)?
- **Objectivity**: is there an evident interest or stance?
- **Date**: when was it produced, and is it dated at all?
- **Significance**: does it add something the other sources do not?

Additional cautions:

- **Vendor and advocacy research** usually answers the question its sponsor wanted
  asked. Use the data; treat the framing and conclusions with reserve.
- **Journalism** is a pointer to a primary source. Find and cite the primary source.
- **Content written to rank in search results** often restates other pages without a
  traceable origin. If a claim has no origin, it is not evidence.
- **Expert opinion** is evidence about what experts think. It supports low certainty at
  most unless the expert shows the underlying data.
- **Preprints** have not been peer reviewed; check whether a published version exists and
  whether its results differ.
- **Internal documents** can establish what an organisation did or recorded. They cannot
  serve as independent confirmation of that organisation's own claims.
- **AI-generated summaries**, including search engine overviews and prior model output,
  are never sources. Trace to the original or drop the claim.

Check for corrections and retractions on any source that a main claim depends on.

## Lineages

Give every included source a `lineage`. Two sources share a lineage when the observation
they report has a single origin:

- several reports of one study (protocol, preprint, article, follow-up, conference talk);
- several papers analysing the same dataset or cohort;
- news articles, blogs and summaries deriving from one original;
- a review and the primary studies it contains, when both are cited for the same claim;
- reports from the same organisation restating its own earlier figures.

Certainty depends on how many lineages stand behind a claim, not how many citations.
`ledger.py ceilings` counts them. The same research team or funder does not by itself
merge two lineages, but record it as a concern when a claim rests wholly on one team.

When unsure whether two sources are independent, ask: if the first were wrong, would the
second be wrong for the same reason? If yes, they share a lineage.

## Access levels

Record how the source was read:

| Value | Meaning | Consequence |
| --- | --- | --- |
| `full-text` | The whole source was read | Can count as sound support |
| `abstract-only` | Only the abstract or summary was available | Never counts as sound support: a claim resting only on such sources is capped at low |
| `secondary-citation` | Known only through another source's account | As above; write "as reported by" |

Abstracts routinely overstate results and omit limitations. State in the report how many
sources were not read in full.

## Assigning the rating

| Rating | Typical profile |
| --- | --- |
| `high` | Design fits the claim; no serious concerns; transparent method; direct to the question |
| `moderate` | Sound overall with one notable concern, or sound but somewhat indirect |
| `low` | Several concerns, or a design that can only suggest and not establish the claim |
| `very-low` | Serious flaws, opaque method, strong interest, or anecdote |

No single weak point is automatically fatal; judge the whole. A fatal flaw is one that
could by itself produce the reported result (for example, groups that differed at the
start in the outcome being measured).

## Field-specific rating schemes

Where a field has an established scheme for rating studies or bodies of evidence, report
its rating alongside this skill's rating and name the scheme. Examples: Cochrane and
GRADE in health; the Education Endowment Foundation's padlock security ratings and What
Works Clearinghouse standards in education; Campbell Collaboration reviews in social
policy; the Maryland Scientific Methods Scale in crime and economic evaluation. Do not
convert one scheme into another as if they were the same scale.
