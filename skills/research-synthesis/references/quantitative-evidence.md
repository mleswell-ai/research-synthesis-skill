# Quantitative evidence

## Contents

- Reporting an effect
- Why vote counting fails
- Comparing effect sizes across studies
- Pooling: when and when not
- Heterogeneity
- Publication and reporting bias
- Common misreadings
- Arithmetic

## Reporting an effect

Every reported effect needs five things, or the reader cannot interpret it:

1. **Size**, in a named metric (mean difference, standardised mean difference, risk
   ratio, odds ratio, correlation, percentage-point change).
2. **Precision**: a confidence interval, or failing that the sample size and standard
   error.
3. **Comparison**: against what.
4. **Outcome and time point**: measured how, and when.
5. **Locator**: the table, figure or page it came from.

Extract effects as reported. Do not convert, round aggressively or recompute unless
necessary; when converting, show the working and mark the figure as derived.

Where sources give both, prefer absolute effects alongside relative ones. "Risk halved"
means little without the baseline: from 2% to 1% and from 40% to 20% are both halvings.

## Why vote counting fails

Counting studies as "significant" or "not significant" and declaring the majority the
winner is unreliable because:

- significance depends on sample size, so small studies of a real effect count as
  "no effect";
- it ignores the size of effects entirely;
- it ignores study quality;
- several underpowered non-significant studies can together show a clear effect.

Acceptable alternatives, in order of preference:

1. Pool the effect estimates (meta-analysis) when studies are similar enough.
2. Summarise effect estimates: report the median and range of effects, with a table or
   plot.
3. Vote count on **direction of effect** only (how many favour the intervention,
   regardless of significance), stated as such and with the number of studies.

State which of these was used.

## Comparing effect sizes across studies

Standardised effect sizes are not a common currency. The same intervention produces a
different standardised effect depending on:

- **the outcome measure**: tests designed around the intervention's content give much
  larger effects than broad standardised tests;
- **the sample**: restricted or homogeneous samples have smaller standard deviations and
  so larger standardised effects;
- **the comparison**: against no treatment gives larger effects than against an active
  alternative;
- **study design and size**: small and non-randomised studies report larger effects on
  average;
- **duration and dose**.

So do not rank interventions by effect size across studies that differ on these features,
and treat generic thresholds for "small", "medium" and "large" as uninformative.
Interpret an effect against benchmarks from comparable studies in the same field, and
against what the difference means in practice.

## Pooling: when and when not

Pool only when the studies address the same question closely enough that an average is
meaningful: comparable populations, interventions, comparisons and outcomes. If asked
whether an average would mean anything and the honest answer is no, do not compute one.

When pooling:

- Use a random-effects model unless there is a clear reason to assume one true effect.
- Report the pooled estimate, its confidence interval, the number of studies and
  participants, and the heterogeneity statistics.
- Check that no study enters twice (overlapping samples, multiple reports).
- Run it with code, not mental arithmetic, and keep the code.

Prefer an existing high-quality meta-analysis to a new one built in passing. When
reporting someone else's pooled estimate, appraise the review and report its
heterogeneity.

## Heterogeneity

Variation in effects between studies beyond what chance explains.

- **I-squared** describes the proportion of observed variation due to real differences
  and not chance. It is not a measure of how much effects differ in absolute terms.
- **A prediction interval** shows the range within which the effect in a new setting is
  likely to fall, and is usually the more useful figure for a decision-maker.
- High heterogeneity means the average hides important differences. Explore why
  (subgroups, moderators), and report the pooled figure with caution or not at all.

Subgroup findings not specified in advance are exploratory. Say so.

## Publication and reporting bias

Studies with positive, significant results are more likely to be published, published
quickly, published in English and cited. Within studies, favourable outcomes are more
likely to be reported.

Practical checks:

- Search trial registers, preprint servers, theses and grey literature.
- Compare registered or protocol outcomes with reported outcomes where available.
- Notice when the evidence consists only of small positive studies.
- Notice when larger or independent studies find smaller effects than small or
  developer-led ones.
- Funnel plots and related tests are informative only with around ten or more studies.

When bias is likely, lower the certainty and say that the true effect is probably smaller
than the published evidence suggests.

## Common misreadings

| Misreading | Correction |
| --- | --- |
| "Not significant, so no effect" | An imprecise estimate is compatible with an effect; report the interval |
| "Significant, so important" | Significance says nothing about size; report the size |
| "Correlated, so causal" | Report as association unless the design supports a causal claim |
| "p = 0.04, so 96% likely to be true" | A p-value is not the probability that the hypothesis is true |
| "The interval excludes zero, so the effect is the point estimate" | Any value in the interval is compatible with the data |
| "Relative change" quoted without baseline | Give absolute figures |
| Percentages and percentage points confused | From 10% to 15% is 5 points, or a 50% rise |
| Group-level result applied to individuals | An average effect does not describe each person |
| Results from one population carried to another | Mark as indirect and lower certainty |
| Surrogate outcomes treated as the real outcome | State which outcome was measured |

## Arithmetic

Do any calculation with code and keep the working. Record derived figures in the ledger
with `kind: "data"`, a locator naming the source figures used, and the word "derived" in
the text. Check that totals, percentages and denominators reconcile before reporting them.
