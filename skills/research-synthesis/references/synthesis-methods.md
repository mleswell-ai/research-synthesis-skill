# Synthesis methods

## Contents

- Choosing a method
- Thematic synthesis (default)
- Narrative synthesis of quantitative evidence
- Framework synthesis
- Realist synthesis
- Meta-ethnography
- Mixed-methods integration
- Scoping and mapping
- What follows for the decision
- Handling contradiction

## Choosing a method

| The question asks | The evidence is | Use |
| --- | --- | --- |
| Does it work, and by how much? | Similar quantitative studies | Meta-analysis (see quantitative-evidence.md) |
| Does it work, and by how much? | Quantitative but too varied to pool | Narrative synthesis with structured effect summary |
| What is going on, how, why? | Qualitative or mixed | Thematic synthesis |
| How does the evidence bear on these known categories? | Any, with a pre-existing framework | Framework synthesis |
| What works, for whom, in what circumstances? | Varied, on a complex intervention | Realist synthesis |
| What new understanding emerges across studies? | A small set of rich qualitative studies | Meta-ethnography |
| What exists and where are the gaps? | Broad and heterogeneous | Scoping or mapping |
| Effect plus experience or implementation | Both strands | Mixed-methods integration |

If unsure, use thematic synthesis and state the choice. Name the method in the report: it
tells the reader how the conclusions were reached.

## Thematic synthesis (default)

Three stages, in order. Do not start with a set of headings and file evidence under them;
that produces a topic list.

1. **Code.** Go through the extracted evidence item by item and label what each one says
   in a few words, staying close to the source's meaning. Let codes multiply at this
   stage. Code evidence that cuts against expectations as carefully as evidence that fits.
2. **Group into descriptive themes.** Bring together codes that describe the same
   underlying thing across different sources. Group on shared meaning, not shared
   vocabulary: two sources may use the same word for different things and different words
   for the same thing.
3. **Develop analytical claims.** For each group ask: what does this evidence, taken
   together, tell us about the question that no single source states? Write the answer as
   a sentence that could be wrong. This step is where synthesis happens; stopping at
   stage 2 yields a well-organised summary.

Tests for a finished claim:

- It is a statement, not a noun phrase.
- Someone could disagree with it.
- It says something about the question, not just about the sources.
- It rests on more than one independent source, or is marked as resting on one.
- A reader could guess the implication from the claim.

## Narrative synthesis of quantitative evidence

For effectiveness questions where studies differ too much to pool. To keep it from
becoming impressionistic:

1. **Tabulate** each study: design, sample, context, intervention, comparison, outcome
   measure, effect estimate with interval, appraisal rating.
2. **Group** studies in a way fixed in advance or justified explicitly (by intervention
   type, population, outcome or design). State the grouping.
3. **Use one standardised metric per outcome** where possible, and describe the range and
   distribution of effects in each group (median, range, direction).
4. **Explore differences**: do effects vary with study quality, dose, duration, setting or
   population? Treat such patterns as hypotheses unless they were specified in advance.
5. **Weigh by quality and precision.** Say which studies carry most weight and why.
6. **Report limitations of the synthesis itself**, including what could not be combined.

Never summarise by counting how many studies were statistically significant. See
quantitative-evidence.md.

## Framework synthesis

Use when a framework, model or set of decision criteria already exists (a policy
framework, a logic model, the user's own evaluation criteria).

1. State the framework and where it comes from.
2. Chart each piece of evidence against its categories in a matrix (sources as rows,
   categories as columns).
3. Note evidence that fits no category, and revise the framework if such evidence is
   substantial. This is the "best fit" step; without it the framework hides whatever it
   did not anticipate.
4. Write claims per category and across categories.

## Realist synthesis

Use for complex interventions whose results depend on context. The unit is the
context-mechanism-outcome configuration: in context C, the intervention triggers
mechanism M, producing outcome O.

1. Set out the initial programme theories: how is this supposed to work?
2. Search purposively for evidence that tests or refines each theory, from any design.
3. Judge each piece on relevance to the theory and rigour for the inference drawn.
4. Refine the configurations. The output is conditional: "works when..., through...,
   and not when...".

## Meta-ethnography

Use for a small number of conceptually rich qualitative studies when the aim is new
interpretation. Identify each study's key concepts, translate them into one another
(noting where they agree, refute or build a line of argument), then express the synthesis
as a higher-order interpretation. Keep the authors' concepts distinguishable from the new
ones.

## Mixed-methods integration

Synthesise each strand with its own method first, then integrate deliberately:

- **Convergence**: do the strands point the same way?
- **Complementarity**: does the qualitative strand explain how or why the quantitative
  effect occurs, or for whom it does not?
- **Dissonance**: where they conflict, which is more direct and trustworthy for this
  part of the question?

A joint display (a table with quantitative findings in one column and the qualitative
evidence that bears on each in the next) makes integration visible.

## Scoping and mapping

The product is a map, not an effect estimate. Chart sources by the dimensions that matter
(topic, population, design, setting, period, outcome), report counts per cell and identify
where evidence is dense, thin or absent. Do not draw conclusions about effectiveness from
a map; say what kind of review would be needed to do so.

## What follows for the decision

A claim earns its place by bearing on the decision. For each main claim write:

- **So what**: what it means for the decision named in the protocol.
- **Options**: more than one way to respond where possible, including not acting.
- **Cost of being wrong**: what happens if the claim is false and it was acted on.
- **What would change this**: the evidence that would overturn it.

Enter these in the ledger as `interpretation` or `recommendation` claims with `based_on`
naming the findings beneath them. They cannot be rated above the weakest of those. If the evidence does not discriminate between options, say so; a forced
recommendation is worse than an honest "the evidence does not settle this".

## Handling contradiction

When sources conflict, work through possible causes before reporting a split:

| Possible cause | Check |
| --- | --- |
| Different populations or settings | Compare samples and contexts |
| Different versions of the intervention | Compare dose, duration, fidelity, delivery |
| Different outcomes or measures | Proximal against distal; self-report against observed |
| Different time horizons | Immediate against delayed follow-up |
| Different comparison conditions | Nothing, business as usual, or an active alternative |
| Different study quality | Do weaker designs give the larger effects? |
| Different interests | Developer-led or funded studies against independent ones |
| Chance | Small studies with wide intervals may not truly conflict |

Then write the outcome in the contradicting item's `reconciled` field. It will be one of
three things: a moderator resolves it (restate the claim conditionally); one side is
better evidence (say why); or it is `unexplained` (which lowers the ceiling). Do not present two unequal bodies of evidence as an even debate.
