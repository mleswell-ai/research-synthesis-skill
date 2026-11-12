"""Rule catalogue and the issue records that rules produce.

Every problem the tool can report has a code. `python scripts/ledger.py explain CODE`
prints why the rule exists and what to do about it.
"""

from __future__ import annotations

from dataclasses import dataclass

ERROR, WARNING = "error", "warning"

# code: (severity, title, why the rule exists and how to respond)
CATALOGUE: dict[str, tuple[str, str, str]] = {
    # Structure
    "S01": (ERROR, "Ledger header incomplete",
            "The question, as_of date, mode, protocol, sources and claims frame everything else. "
            "Fill them in; as_of is the date the evidence was gathered, as YYYY-MM-DD."),
    "S02": (ERROR, "Identifier malformed or repeated",
            "Sources are S1, S2 (a worker letter is allowed: SA1); claims are C1, C2. Each must be "
            "unique or citations become ambiguous."),
    "S03": (ERROR, "Source record incomplete",
            "A reader must be able to find the source and know how it was read. Supply title, year "
            "(\"n.d.\" if undated), ref, type, access and status, using the allowed values."),
    "S04": (ERROR, "Excluded source has no reason",
            "Exclusions are part of the method. Name the criterion the source failed."),
    "S05": (ERROR, "Included source has no lineage or appraisal",
            "Lineage is how repeated reports of one observation get counted once; appraisal is how "
            "much weight the source can bear. Both are needed to compute certainty ceilings."),
    "S06": (WARNING, "Appraisal lowered without stated concerns",
            "A rating below high should say what lowered it, so the reader can disagree."),
    "S07": (ERROR, "Claim record incomplete",
            "Each claim needs a statement, type, theme, certainty and rationale, using the allowed values."),
    # Protocol
    "P01": (ERROR, "Corpus not declared",
            "State whether the sources were supplied, searched for, or both. It decides whether a "
            "search log is expected and what the report may claim about coverage."),
    "P02": (ERROR, "Systematic mode without inclusion criteria",
            "A systematic synthesis fixes its criteria before reading. Record them."),
    "P03": (ERROR, "Systematic mode without a search log",
            "A systematic search must be repeatable: log where, query, date and results for each search."),
    "P04": (WARNING, "Searched corpus without a search log",
            "Log each query so the report can describe the search honestly."),
    "P05": (WARNING, "Search log entry incomplete",
            "Each entry needs where and date as well as the query."),
    # Evidence
    "E01": (ERROR, "Evidence cites an unknown source",
            "Add the source to the ledger after reading it, or remove the evidence item. A citation "
            "to a source that is not in the ledger is how invented references get in."),
    "E02": (ERROR, "Evidence cites an excluded source",
            "Evidence may come only from included sources. Include the source (and appraise it) or "
            "drop the item."),
    "E03": (ERROR, "Evidence item incomplete",
            "Every item needs a locator, the text (quotation, paraphrase or figure with units) and a "
            "kind of quote, paraphrase or data."),
    "E04": (ERROR, "Finding has no usable support",
            "A finding reports what sources say, so it needs at least one evidence item from an "
            "included source."),
    "E05": (ERROR, "Derived claim has no valid basis",
            "An interpretation or recommendation must name the claims it follows from in based_on "
            "(or carry evidence of its own), and those claims must exist."),
    "E06": (WARNING, "Included source is unused",
            "The source bears on no claim. Extract its evidence, or exclude it with a reason."),
    "E07": (WARNING, "Quotation is long",
            "Long verbatim passages add little; quote the decisive words and paraphrase the rest."),
    "E08": (WARNING, "No contrary evidence recorded anywhere",
            "With five or more sources, total agreement usually means contrary evidence was not "
            "looked for. Search for it and record what turns up, including nothing."),
    "E09": (WARNING, "Whole synthesis rests on one lineage",
            "Every included source traces to the same origin, so there is no independent check."),
    # Certainty
    "C01": (ERROR, "Certainty exceeds what the evidence can carry",
            "The stated rating is above the ceiling computed from lineages, appraisals, access and "
            "unreconciled contradictions. Lower the rating, or add evidence that raises the ceiling. "
            "Run `ledger.py ceilings` to see the binding constraint."),
    "C02": (ERROR, "Derived claim is more certain than its basis",
            "An interpretation or recommendation adds an inferential step, so it cannot be rated "
            "above the weakest claim it depends on."),
    "C03": (WARNING, "Contradiction not reconciled",
            "Say in `reconciled` how the claim accounts for this evidence (a moderator, weaker "
            "design, different outcome) or write \"unexplained\". Unreconciled contradictions lower "
            "the ceiling."),
    # Verification
    "V01": (ERROR, "Evidence failed its check against the source",
            "An item is marked mismatch: the source does not say this at the locator. Correct the "
            "item (and the claim if needed), then mark it confirmed."),
    "V02": (WARNING, "Evidence awaiting confirmation",
            "Quotations, figures and keystone evidence must be re-read at the locator and marked "
            "confirmed before the report is final. Run `ledger.py worksheet`."),
    "V03": (ERROR, "Unknown check state",
            "`checked` may be confirmed or mismatch, or absent."),
    "V04": (ERROR, "Report finalised with unconfirmed evidence",
            "Outside rapid mode a report cannot pass while required evidence is unconfirmed."),
    # Report
    "R01": (ERROR, "Report section missing",
            "The reader needs a bottom line, findings, gaps and limitations, a source list and "
            "(outside rapid mode) an account of method."),
    "R02": (ERROR, "Report cites a source that is not in the ledger",
            "Add the source to the ledger after reading it, or remove the citation."),
    "R03": (ERROR, "Report cites an excluded source", "Cite included sources only."),
    "R04": (ERROR, "Report has no citations", "Cite sources as [S1] directly after what they support."),
    "R05": (ERROR, "Report refers to an unknown claim", "Claim references such as [C3] must exist in the ledger."),
    "R06": (ERROR, "Placeholder or template text remains", "Replace or remove it."),
    "R07": (ERROR, "Findings are not separated",
            "Give each finding its own sub-heading, written as a full-sentence claim."),
    "R08": (ERROR, "Finding has no certainty rating",
            "Add a line such as `Certainty: Moderate. <reason>` under the heading."),
    "R09": (ERROR, "Finding has no citation", "Each finding must cite the sources it rests on."),
    "R10": (ERROR, "Report and ledger disagree on certainty",
            "The ledger is the record; make the report match it, or revise the ledger first."),
    "R11": (WARNING, "Finding not linked to a ledger claim",
            "Put the claim id, for example [C1], in the finding's heading."),
    "R12": (WARNING, "Ledger finding missing from the report",
            "Report it, or remove it from the ledger. Dropping inconvenient findings is a bias."),
    "R13": (WARNING, "Included source never cited in the report",
            "Cite it, or exclude it in the ledger with a reason."),
    "R14": (WARNING, "Cited source missing from the source list", "List every cited source by id."),
    "R15": (WARNING, "Claim of support with no source",
            "Phrases such as \"studies show\" need a citation in the same sentence, with a count."),
    "R16": (WARNING, "Figure with no source",
            "A number in the findings needs a citation in its paragraph."),
}


@dataclass(frozen=True)
class Issue:
    code: str
    where: str
    message: str

    @property
    def severity(self) -> str:
        return CATALOGUE[self.code][0]

    def line(self) -> str:
        return f"{self.severity.upper():7} {self.code} {self.where}: {self.message}"

    def as_dict(self) -> dict:
        return {"code": self.code, "severity": self.severity, "where": self.where, "message": self.message}


def errors(issues: list[Issue]) -> list[Issue]:
    return [i for i in issues if i.severity == ERROR]


def warnings(issues: list[Issue]) -> list[Issue]:
    return [i for i in issues if i.severity == WARNING]


def catalogue_table() -> str:
    """The catalogue as a Markdown table (used in references/evidence-ledger.md)."""
    rows = ["| Code | Severity | Rule |", "| --- | --- | --- |"]
    rows += [f"| {code} | {sev} | {title} |" for code, (sev, title, _) in CATALOGUE.items()]
    return "\n".join(rows)
