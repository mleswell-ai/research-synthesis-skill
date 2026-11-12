# Rating certainty

## Contents

- What the rating means
- Procedure for findings about effects and associations
- Ceilings
- Qualitative findings
- Claims resting on non-research sources
- Interpretations and recommendations
- Wording by rating
- Writing the rationale
- Worked examples

## What the rating means

Certainty is a judgement about a **claim**, given the whole body of evidence for it. It is
separate from the appraisal of any single source. Several moderate sources that agree may
give high certainty; one excellent source alone usually does not.

| Rating | Meaning |
| --- | --- |
| High | Very confident the claim is right; further evidence is very unlikely to change it |
| Moderate | Fairly confident; further evidence could change it |
| Low | Limited confidence; the truth may well differ |
| Very low | Little confidence; the claim is a possibility, not a conclusion |

The approach below follows the logic of GRADE (for quantitative evidence) and
GRADE-CERQual (for qualitative evidence), simplified for general use. In Systematic mode
in a field that uses those systems formally, apply them in full and say so.

## Procedure for findings about effects and associations

**1. Set the starting point** from what the best available evidence can support:

| Body of evidence | Start |
| --- | --- |
| Randomised or otherwise well-controlled experimental studies, or sound systematic reviews of them | High |
| Observational, quasi-experimental or correlational studies | Low |
| Case reports, expert opinion, unsystematic observation | Very low |

**2. Move down** one level (two if serious) for each of:

- **Risk of bias**: the supporting studies have limitations that could produce the result.
- **Inconsistency**: results differ across studies without a good explanation.
- **Indirectness**: the population, intervention, comparison or outcome differs from the
  question; or the comparison is indirect.
- **Imprecision**: few participants or events; wide intervals that include both a
  meaningful effect and none.
- **Publication or selection bias**: reason to think missing evidence would change the
  picture.

**3. Move up** one level, where there are no serious concerns above, for:

- a **large effect** that bias is unlikely to explain;
- a **dose-response** pattern;
- plausible confounding that would **reduce** the observed effect, yet the effect remains.

**4. Stay under the ceiling.** Steps 1 to 3 are judgement. The ceiling is arithmetic on
the ledger, and the judgement may not exceed it.

## Ceilings

`python scripts/ledger.py ceilings ledger.json` computes, for each claim, the highest
certainty its recorded evidence can carry.

**Sound support** means a source appraised moderate or better and read in full.

| The claim's support includes | Ceiling |
| --- | --- |
| Sound support from two or more lineages | High |
| A sound systematic review or meta-analysis | High |
| Sound support from one lineage only | Moderate |
| No sound support (weak sources, abstracts, second-hand reports) | Low |
| Only sources appraised very-low | Very low |

Then two adjustments:

- **Unreconciled contradiction.** A contradicting item with no `reconciled` text, or
  marked `unexplained`, lowers the ceiling to moderate. If its source is appraised at
  least as highly as the best supporting source, the ceiling is low.
- **Derived claims.** An interpretation or recommendation takes the certainty of the
  weakest claim it is `based_on` as its ceiling.

What the ceiling is not:

- It is not a rating. Two sound lineages allow high; whether the claim deserves it
  depends on bias, consistency, directness and precision. In the worked example, a claim
  with a ceiling of high is rated low because both intervals reach zero.
- It does not read the evidence. It cannot tell whether a source's support is strong or
  incidental. That is what the `rationale` and the re-reading step are for.
- It is deliberately conservative about single sources. One excellent trial gives
  moderate at most until something independent agrees with it.

`python scripts/ledger.py keystones ledger.json` then shows which lineages each rating
depends on: remove a keystone and the claim loses its evidence, or its ceiling drops
below the stated rating. Those are the sources to scrutinise first.

## Qualitative findings

Assess four components, then judge overall:

| Component | Question | Lowers confidence when |
| --- | --- | --- |
| Methodological limitations | How sound are the contributing studies or data? | Recruitment, collection or analysis is weak or unreported |
| Coherence | How well does the finding fit the data behind it? | Data are ambiguous, or contradicting cases are unexplained |
| Adequacy | How rich and plentiful are the data? | Few participants, thin description, one site |
| Relevance | How well do the contexts match the question? | Different setting, population or period |

Start at high and lower for each component with serious concerns. For primary qualitative
data from a single project, adequacy and relevance usually cap the rating at moderate for
claims about the group studied, and lower for claims that reach beyond it.

## Claims resting on non-research sources

For questions about markets, technology, organisations, policy or current events, where
the evidence is documents, statistics, reporting and expert testimony, use the same logic
with these considerations:

| Consideration | Raises | Lowers |
| --- | --- | --- |
| Directness of access | First-hand records, official statistics, original documents | Hearsay, summaries, unattributed claims |
| Independence | Several unrelated sources with separate access | One origin repeated by many |
| Interest | Source gains nothing from the answer, or reports against its interest | Vendor, advocate or party to a dispute |
| Method transparency | Stated and checkable | Opaque |
| Currency | Recent relative to how fast the subject changes | Possibly overtaken |
| Specificity | Dated, quantified, attributable | Vague |

Typical outcomes: official statistics or original records confirmed by an independent
source support high; a single credible first-hand source supports moderate; reporting
without a traceable origin, or a single interested source, supports low at most.

## Interpretations and recommendations

An interpretation or recommendation can be no more certain than the findings it rests on,
and is usually less certain, because it adds an inferential step. The tool enforces the
first part (rule C02); the second is judgement. State the step in the rationale.

## Wording by rating

Use the wording consistently so that the reader can tell ratings apart from the prose
alone.

| Rating | Effect or association | Qualitative or descriptive |
| --- | --- | --- |
| High | "X improves Y." | "Participants consistently..." / "The records show..." |
| Moderate | "X probably improves Y." | "It is likely that..." |
| Low | "X may improve Y." | "There are indications that..." |
| Very low | "It is unclear whether X improves Y; the evidence is very uncertain." | "A few accounts suggest..., which is too little to rely on." |

For size, add "slightly", "substantially" and so on, based on the estimate and what the
difference means in practice, not on significance. Where there is no evidence at all, say
"no evidence was found on..." and describe the search; do not write "there is no
evidence that", which reads as a negative finding.

## Writing the rationale

One sentence naming what set the rating. State the start point and each move.

Good: "Moderate: three randomised trials with consistent direction, lowered one level
because all measured outcomes with tests aligned to the programme."

Poor: "Moderate: based on several good studies."

## Worked examples

**Effectiveness.** Claim: a tutoring programme improves attainment. Evidence: four
randomised trials (start high). Three are developer-led with programme-aligned tests
(risk of bias and indirectness: down one). Effects range from near zero to large with no
clear explanation (inconsistency: down one). Rating: low. Wording: "The programme may
improve attainment; effects vary widely and the most independent trial found the
smallest."

**Association.** Claim: an exposure is associated with an outcome. Evidence: five large
cohort studies (start low), consistent, with a clear dose-response pattern (up one).
Rating: moderate. Wording: "Higher exposure is probably associated with...", with no
causal language beyond what the designs allow.

**Qualitative.** Claim: new staff do not know whom to ask for help in the first weeks.
Evidence: 11 of 16 interviewees across three sites, with specific incidents; two
contradicting cases explained by an assigned mentor. Coherence and adequacy sound;
relevance direct. Rating: high for these sites; moderate if generalised to the
organisation as a whole.

**Non-research.** Claim: a regulator changed a requirement on a given date. Evidence: the
regulator's published notice, read in full, plus an independent trade-press report.
Rating: high. The same claim supported only by a consultancy blog: low, pending the
original notice.
