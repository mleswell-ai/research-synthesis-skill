# research-synthesis

An agent skill for Claude that turns a set of sources into a synthesis you can check and
act on. It covers literature and evidence reviews (rapid, scoping, systematic-style),
synthesis of interviews and other qualitative data, and audits of existing reviews.

## The idea

Every statement in the output has to survive three questions:

1. **Where exactly does this come from?** A located passage in a source that was read.
2. **How many separate times was it observed?** Ten articles repeating one study are one
   observation. Sources that trace to one origin share a **lineage**.
3. **How sure does that allow us to be?** The structure of the evidence sets a
   **ceiling** on certainty. Judgement can rate a claim lower, never higher.

The answers live in an **evidence ledger**, one JSON file of sources, claims and the
evidence for and against each claim. A small tool, `ledger.py`, reads it and does the
parts a machine can do:

```console
$ python scripts/ledger.py ceilings examples/flexible-start/ledger.json
C1  stated low        ceiling high      below ceiling
      - two or more sound lineages, or a sound review, and no unreconciled contradiction
C2  stated low        ceiling moderate  below ceiling
      - sound support comes from one lineage (L4); high needs a second independent lineage or a sound systematic review
C3  stated very-low   ceiling low       below ceiling
      - sound support comes from one lineage (L1); high needs a second independent lineage or a sound systematic review
      - unreconciled contradiction from S5, appraised at least as highly as the best supporting source
C4  stated low        ceiling low       at ceiling
      - no supporting source is both appraised moderate or better and read in full

$ python scripts/ledger.py keystones examples/flexible-start/ledger.json
C2  L4 (S5): sole support: without it the claim has no evidence
...
Check these sources first, and hardest:
  S5  carries C2, C5  Flexible start times in distribution: an 18-month matched evaluation
```

## What it guards against

| Common failure | Mechanism here |
| --- | --- |
| Invented or mismatched citations | A report may cite only ledger sources. Figures, quotations and keystone evidence go on a **worksheet** to be re-read at the locator and marked `confirmed` or `mismatch`; a report cannot pass with any outstanding |
| One study counted many times | **Lineages**. Press coverage, preprints and re-analyses of one study count once |
| Confident claims on thin evidence | **Ceilings**. One lineage allows moderate at most; abstracts and second-hand reports allow low at most |
| Disagreement glossed over | Each contradicting item needs a `reconciled` explanation or the word `unexplained`; unreconciled contradictions lower the ceiling |
| Conclusions resting on one source nobody re-checked | **Keystones**: the lineages each rating depends on, listed for scrutiny first |
| Opinion presented as finding | Findings, interpretations and recommendations are separate claim types; a recommendation cannot be more certain than the weakest finding under it |
| Source-by-source summary | Findings are full-sentence claims that could be wrong, each drawing on several sources |
| "Studies show..." | Flagged wherever it appears without a citation in the same sentence |
| A report nobody can act on | Answer first, tied to the decision, including "do not act" and "the evidence cannot decide this" |

## Contents

```
skills/research-synthesis/
├── SKILL.md                       The three questions; nine-step workflow; three modes
├── scripts/
│   ├── ledger.py                  new, check, ceilings, keystones, worksheet, mark,
│   │                              trace, tables, report, explain
│   └── ledgerkit/                 schema, 44 coded rules, ceiling and keystone logic,
│                                  report rules, views (Python standard library only)
├── references/                    Read only when needed
│   ├── scoping-and-protocol.md    Question frameworks, review types, protocol
│   ├── source-appraisal.md        Appraisal by design, grey literature, lineages, access
│   ├── evidence-ledger.md         Ledger fields, commands, rule codes
│   ├── synthesis-methods.md       Thematic, narrative, framework, realist, mixed methods
│   ├── quantitative-evidence.md   Effect sizes, pooling, heterogeneity, reporting bias
│   ├── qualitative-data.md        Six passes through interview and feedback data
│   ├── certainty.md               Rating procedure, ceiling rules, wording, examples
│   ├── parallel-research.md       Delegating to subagents: briefs, merging, review
│   ├── failure-modes.md           36 failures with symptom, cause and fix
│   └── quality-rubric.md          Eight dimensions with a pass mark
├── assets/                        Report and rapid-brief templates
└── examples/flexible-start/       A complete ledger, report and tables
evals/                             Four scenarios with planted traps; trigger queries
tests/                             54 tests for the tool
```

## Install

**Claude Code** (personal, available in every project):

```bash
git clone https://github.com/mleswell-ai/research-synthesis-skill.git
mkdir -p ~/.claude/skills
cp -r research-synthesis-skill/skills/research-synthesis ~/.claude/skills/
```

For one project only, copy the folder to `.claude/skills/` in that project instead.

**Claude apps (claude.ai and desktop)**: build the ZIP, or take it from the
[latest release](https://github.com/mleswell-ai/research-synthesis-skill/releases/latest):

```bash
cd research-synthesis-skill/skills && zip -r research-synthesis.zip research-synthesis
```

Then **Customize > Skills**, **+**, **Create skill**, **Upload a skill**. Code execution
and file creation need to be on for the tool to run. Menu names change; see
[Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

**Other agents** that support the Agent Skills format can load
`skills/research-synthesis` as it is.

## Use

Ask in ordinary language:

- "What does the research say about X? I need to decide whether to..."
- "Synthesise these twelve papers and tell me how solid the conclusions are."
- "Here are our interview transcripts. What are the findings?"
- "These three reports contradict each other. Reconcile them."
- "Check whether this literature review holds up."

The skill picks a mode (Rapid, Standard, Systematic) to fit; say which you want if you
have a preference. The tool also works by hand:

```bash
python scripts/ledger.py new ledger.json --question "..." --mode standard --corpus searched
python scripts/ledger.py check ledger.json            # --strict, --urls, --json
python scripts/ledger.py ceilings ledger.json
python scripts/ledger.py keystones ledger.json
python scripts/ledger.py worksheet ledger.json
python scripts/ledger.py mark ledger.json confirmed C1.s1 C1.s2
python scripts/ledger.py trace ledger.json C1
python scripts/ledger.py report report.md ledger.json
python scripts/ledger.py explain C01
```

## What the tool cannot do

It cannot read a source and tell whether it says what is claimed. The worksheet makes the
model do that re-reading item by item and record the result, and `report` refuses to pass
until it has, but the record is the model's own. For anything a decision rests on, run
`keystones` and check those sources yourself. No skill removes the need for that.

Ceilings are limits computed from how the evidence is structured. They do not judge how
good the evidence is; that remains a judgement, written down in each claim's rationale.

## Testing and status

```bash
python -m unittest discover -s tests -v
```

- **The tool** is covered by 54 tests, including one that checks every figure in the
  worked example against the document it cites.
- **The worked example** was produced by following the skill end to end on the documents
  in `evals/files/flexible-start/`.
- **The evaluation scenarios** in `evals/evals.json` (a supplied corpus, interview notes,
  an audit, an open question) each plant specific traps and list the expected behaviour.
  There is no built-in runner. Results from running them across models, with and without
  the skill, are not yet published here, so the size of the improvement is unmeasured.

All evaluation and example material is fictitious. Reports of where the skill falls
short are welcome as issues.

## How this relates to other research skills

Several published skills cover neighbouring ground, and this one was written after
studying them. None of their text or code is used. What was learned from each:

| Skill or source | Idea taken forward |
| --- | --- |
| [Anthropic: skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | A lean core file with references one level deep; check-fix-repeat loops; evaluations |
| [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Explicit briefs for workers; effort scaled to the task; broad-then-narrow search |
| [rampstackco: discovery-research-synthesis](https://github.com/rampstackco/claude-skills/blob/main/skills/discovery-research-synthesis/SKILL.md) | Stages that may not be skipped; "do not act" as a legitimate implication; saying when data are too thin |
| [daymade: deep-research](https://github.com/daymade/claude-code-skills/blob/main/deep-research/SKILL.md) | Binding claims to source ids and locators; weighing by underlying source, not by number of reports |
| [199-biotechnologies: deep-research](https://github.com/199-biotechnologies/claude-deep-research-skill) | Keeping research state on disk; scripted validation |
| [borghei: litreview](https://github.com/borghei/Claude-Skills/blob/main/research/litreview/SKILL.md) | Asking only the questions that change the work; fixing criteria before screening |
| [mohitagw15856: user-research-synthesis](https://github.com/mohitagw15856/pm-claude-skills/blob/main/skills/user-research-synthesis/SKILL.md) | Counts with denominators; keeping observation apart from inference |
| [K-Dense-AI: literature-review](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/literature-review/SKILL.md) | Linking multiple reports of one study; a DOI that resolves is not a correct citation |

What is different here, as far as that comparison shows: certainty ceilings computed from
the evidence structure; lineages as a first-class field that the ceiling depends on;
keystone analysis; reconciliation of contradictions as a field that affects the ceiling;
typed claims with a rule that derived claims cannot outrank their basis; an enforced
re-reading worksheet; and a single tool with coded, self-explaining rules.

A text comparison against those six repositories at release (every six-word sequence in
this skill folder, checked against theirs) found 29 shared sequences out of about 23,500,
or 0.12%. All were Python idioms, standard methodology terms such as GRADE's five
domains, or stock phrases.

The methodology itself is not original and is not claimed to be: PRISMA 2020 and
PRISMA-ScR for reporting; GRADE and GRADE-CERQual for certainty; the Cochrane Handbook on
synthesis without meta-analysis; thematic, framework, realist and meta-ethnographic
synthesis; AMSTAR 2, RoB 2, ROBINS-I, CASP, MMAT and AACODS for appraisal. The skill
simplifies these for general use and says where it does. For a formal systematic review,
apply the originals in full.

## Limitations

- It depends on what the model can reach. Paywalled papers read as abstracts are recorded
  as such and capped at low, which is honest but is not the same as reading them.
- A "systematic" run by one model in one session does not replace a registered,
  dual-screened systematic review. The skill says so in its output.
- The ceiling rules are deliberately simple and conservative. They will sometimes hold a
  well-supported claim at moderate until a second lineage is recorded.

## Licence

[MIT](LICENSE).
