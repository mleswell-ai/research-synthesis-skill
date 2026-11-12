"""Tests for scripts/ledger.py and the ledgerkit package.

Run from the repository root:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "research-synthesis"
TOOL = SKILL / "scripts" / "ledger.py"
FIXTURE = ROOT / "tests" / "fixtures" / "valid"
EXAMPLE = SKILL / "examples" / "flexible-start"

GOOD_LEDGER = json.loads((FIXTURE / "ledger.json").read_text(encoding="utf-8"))
GOOD_REPORT = (FIXTURE / "report.md").read_text(encoding="utf-8")


def tool(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, timeout=60)


class Case(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()
        self.dir = Path(self._dir.name)
        self.ledger = copy.deepcopy(GOOD_LEDGER)
        self.claims = {c["id"]: c for c in self.ledger["claims"]}
        self.sources = {s["id"]: s for s in self.ledger["sources"]}

    def tearDown(self) -> None:
        self._dir.cleanup()

    def save(self, ledger=None) -> str:
        path = self.dir / "ledger.json"
        path.write_text(json.dumps(self.ledger if ledger is None else ledger), encoding="utf-8")
        return str(path)

    def check(self, *flags: str) -> subprocess.CompletedProcess:
        return tool("check", self.save(), *flags)

    def codes(self, *flags: str) -> set:
        result = tool("check", self.save(), "--json", *flags)
        return {i["code"] for i in json.loads(result.stdout)["issues"]}

    def assertClean(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 error(s), 0 warning(s)", result.stdout)


class LedgerStructure(Case):
    def test_fixture_is_clean_under_strict(self):
        self.assertClean(self.check("--strict"))

    def test_evidence_must_cite_a_known_source(self):
        self.claims["C1"]["support"][0]["source"] = "S99"
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("E01 C1.s1", result.stdout)

    def test_evidence_cannot_cite_an_excluded_source(self):
        self.claims["C1"]["support"][0]["source"] = "S6"
        self.assertIn("E02", self.codes())

    def test_evidence_needs_a_locator(self):
        self.claims["C2"]["support"][0]["locator"] = "  "
        result = self.check()
        self.assertIn("E03 C2.s1: missing locator", result.stdout)

    def test_finding_needs_support(self):
        self.claims["C2"]["support"] = []
        self.assertIn("E04", self.codes())

    def test_derived_claim_needs_a_real_basis(self):
        self.claims["C4"]["based_on"] = ["C9"]
        self.assertIn("E05", self.codes())
        self.claims["C4"]["based_on"] = ["C4"]
        self.assertIn("E05", self.codes())

    def test_excluded_source_needs_a_reason(self):
        del self.sources["S6"]["exclusion_reason"]
        self.assertIn("S04", self.codes())

    def test_included_source_needs_lineage_and_appraisal(self):
        del self.sources["S1"]["lineage"]
        self.sources["S2"]["appraisal"] = {"rating": "excellent"}
        result = self.check()
        self.assertIn("S05 S1", result.stdout)
        self.assertIn("S05 S2", result.stdout)

    def test_repeated_ids_are_rejected(self):
        self.sources["S2"]["id"] = "S1"
        self.assertIn("S02", self.codes())

    def test_systematic_mode_needs_a_search_log(self):
        self.ledger["mode"] = "systematic"
        self.ledger["protocol"]["search_log"] = []
        self.assertIn("P03", self.codes())

    def test_supplied_corpus_needs_no_search_log(self):
        self.ledger["protocol"]["corpus"] = "supplied"
        self.ledger["protocol"]["search_log"] = []
        self.assertClean(self.check("--strict"))

    def test_unused_source_and_missing_dissent_are_warnings(self):
        self.claims["C1"]["contradicts"] = []
        self.assertEqual(self.check().returncode, 0)
        self.assertTrue({"E06", "E08"} <= self.codes())
        self.assertEqual(self.check("--strict").returncode, 1)

    def test_single_lineage_synthesis_is_flagged(self):
        for source in self.sources.values():
            if source["status"] == "included":
                source["lineage"] = "L1"
        self.assertIn("E09", self.codes())

    def test_malformed_content_is_reported_not_crashed_on(self):
        self.ledger["sources"].append("not an object")
        self.ledger["claims"].append(42)
        self.claims["C1"]["support"] = "S1"
        self.claims["C2"]["based_on"] = "C1"
        self.ledger["protocol"]["search_log"] = "none"
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")

    def test_unreadable_files(self):
        self.assertEqual(tool("check", str(self.dir / "absent.json")).returncode, 2)
        bad = self.dir / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        result = tool("check", str(bad))
        self.assertEqual(result.returncode, 2)
        self.assertIn("not valid JSON", result.stdout)
        bad.write_text("[]", encoding="utf-8")
        self.assertEqual(tool("check", str(bad)).returncode, 2)

    def test_json_output(self):
        self.claims["C1"]["support"][0]["source"] = "S99"
        payload = json.loads(tool("check", self.save(), "--json").stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["issues"][0]["severity"], "error")


class Ceilings(Case):
    def test_one_lineage_cannot_carry_high(self):
        self.claims["C3"]["certainty"] = "high"  # rests on S4 alone
        result = self.check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("C01 C3: rated high; ceiling is moderate", result.stdout)

    def test_two_reports_of_one_study_count_once(self):
        claim = self.claims["C1"]
        claim["support"] = claim["support"][:2]  # S1 and S2
        claim["contradicts"] = []
        claim["certainty"] = "high"
        self.assertNotIn("C01", self.codes())  # two lineages: allowed
        self.sources["S2"]["lineage"] = "L1"
        self.assertIn("C01", self.codes())      # same lineage: not allowed

    def test_sound_review_can_carry_high_alone(self):
        claim = self.claims["C2"]
        claim["support"] = [claim["support"][1]]  # S3, a systematic review appraised moderate
        claim["certainty"] = "high"
        self.assertNotIn("C01", self.codes())

    def test_abstract_only_support_is_capped_at_low(self):
        self.claims["C3"]["support"] = [
            {"source": "S5", "locator": "Summary", "kind": "paraphrase", "text": "No change", "checked": "confirmed"}]
        self.claims["C3"]["certainty"] = "moderate"
        self.assertIn("C01 C3: rated moderate; ceiling is low", self.check().stdout)

    def test_very_low_sources_cap_at_very_low(self):
        self.sources["S4"]["appraisal"] = {"rating": "very-low", "concerns": ["anecdote"]}
        self.assertIn("ceiling is very-low", self.check().stdout)  # C3 is rated low

    def test_unreconciled_contradiction_lowers_the_ceiling(self):
        claim = self.claims["C1"]
        claim["certainty"] = "high"
        self.assertNotIn("C01", self.codes())           # reconciled: high is allowed
        del claim["contradicts"][0]["reconciled"]
        result = self.check()
        self.assertIn("C01 C1: rated high; ceiling is moderate", result.stdout)
        self.assertIn("C03 C1.x1", result.stdout)

    def test_unexplained_contradiction_from_a_strong_source_caps_at_low(self):
        claim = self.claims["C1"]
        self.sources["S5"]["appraisal"] = {"rating": "high", "concerns": []}
        claim["contradicts"][0]["reconciled"] = "unexplained: neither study tests this"
        result = self.check()
        self.assertIn("C01 C1: rated moderate; ceiling is low", result.stdout)
        self.assertNotIn("C03", result.stdout)  # it was addressed, just not resolved

    def test_recommendation_cannot_outrank_its_weakest_basis(self):
        self.claims["C4"]["certainty"] = "moderate"  # C2 and C3 are low
        self.assertIn("C02 C4: rated moderate; ceiling is low because rests on C2", self.check().stdout)

    def test_ceilings_view_names_the_binding_constraint(self):
        result = tool("ceilings", self.save())
        self.assertEqual(result.returncode, 0)
        self.assertRegex(result.stdout, r"C3\s+stated low\s+ceiling moderate")
        self.assertIn("sound support comes from one lineage (L4)", result.stdout)


class KeystonesAndVerification(Case):
    def test_sole_support_is_a_keystone(self):
        result = tool("keystones", self.save())
        self.assertIn("C3  L4 (S4): sole support", result.stdout)
        self.assertNotIn("C1  ", result.stdout)  # three lineages behind a moderate claim

    def test_lineage_whose_loss_would_break_the_rating_is_a_keystone(self):
        claim = self.claims["C1"]
        claim["support"] = claim["support"][:2]
        claim["certainty"] = "high"
        result = tool("keystones", self.save())
        self.assertIn("C1  L1 (S1): without it the ceiling falls to moderate, below the stated high", result.stdout)
        self.assertIn("C1  L2 (S2)", result.stdout)

    def test_unconfirmed_figures_are_listed_and_warned_about(self):
        del self.claims["C1"]["support"][0]["checked"]
        self.assertIn("V02", self.codes())
        self.assertIn("[ ] C1.s1", tool("worksheet", self.save()).stdout)

    def test_mark_records_the_result(self):
        del self.claims["C1"]["support"][0]["checked"]
        path = self.save()
        self.assertEqual(tool("mark", path, "confirmed", "C1.s1").returncode, 0)
        self.assertClean(tool("check", path, "--strict"))

    def test_mismatch_needs_a_note_and_blocks_the_check(self):
        path = self.save()
        self.assertEqual(tool("mark", path, "mismatch", "C2.s1").returncode, 2)
        self.assertEqual(tool("mark", path, "mismatch", "C2.s1", "--note", "Table 3 gives 0.30").returncode, 0)
        result = tool("check", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("V01 C2.s1", result.stdout)
        self.assertIn("Table 3 gives 0.30", result.stdout)

    def test_mark_rejects_unknown_addresses(self):
        self.assertEqual(tool("mark", self.save(), "confirmed", "C9.s1").returncode, 2)


class NewLedger(Case):
    def test_new_writes_a_dated_skeleton_and_will_not_overwrite(self):
        path = str(self.dir / "sub" / "fresh.json")
        result = tool("new", path, "--question", "Does X improve Y?", "--mode", "rapid", "--corpus", "supplied")
        self.assertEqual(result.returncode, 0, result.stdout)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.assertRegex(data["as_of"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual((data["mode"], data["protocol"]["corpus"]), ("rapid", "supplied"))
        self.assertEqual(tool("new", path, "--question", "again").returncode, 2)


class ReportRules(Case):
    def report(self, text: str, *flags: str) -> subprocess.CompletedProcess:
        path = self.dir / "report.md"
        path.write_text(text, encoding="utf-8")
        return tool("report", str(path), self.save(), *flags)

    def test_fixture_is_clean_under_strict(self):
        self.assertClean(self.report(GOOD_REPORT, "--strict"))

    def test_citation_must_be_in_the_ledger(self):
        result = self.report(GOOD_REPORT.replace("[S3]. Against", "[S3, S42]. Against"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("R02 [S42]", result.stdout)

    def test_excluded_source_cannot_be_cited(self):
        self.assertIn("R03 [S6]", self.report(GOOD_REPORT.replace("at one year [S1]", "at one year [S1, S6]")).stdout)

    def test_required_sections(self):
        without = GOOD_REPORT.replace("## Gaps and limitations", "## Other notes")
        self.assertIn("R01 report: no section for gaps and limitations", self.report(without).stdout)

    def test_rapid_brief_may_omit_the_method(self):
        start, end = GOOD_REPORT.index("## How this was done"), GOOD_REPORT.index("## Sources")
        brief = GOOD_REPORT[:start] + GOOD_REPORT[end:]
        self.assertIn("R01", self.report(brief).stdout)
        self.ledger["mode"] = "rapid"
        self.assertClean(self.report(brief, "--strict"))

    def test_each_finding_needs_a_rating(self):
        result = self.report(GOOD_REPORT.replace("Certainty: Low. One trial with high attrition at follow-up.\n", ""))
        self.assertIn("R08", result.stdout)

    def test_report_and_ledger_must_agree(self):
        result = self.report(GOOD_REPORT.replace("Certainty: Low. One trial", "Certainty: High. One trial"))
        self.assertIn("R10", result.stdout)
        self.assertIn("report says high; ledger rates C2 low", result.stdout)

    def test_templates_are_rejected_until_filled_in(self):
        for name in ("report-template.md", "brief-template.md"):
            result = self.report((SKILL / "assets" / name).read_text(encoding="utf-8"))
            self.assertEqual(result.returncode, 1, name)
            self.assertIn("R06", result.stdout)

    def test_unnamed_support_is_flagged_unless_cited(self):
        marker = "## Where the evidence disagrees\n"
        flagged = self.report(GOOD_REPORT.replace(marker, marker + "\nStudies show that structured programmes work.\n"))
        self.assertEqual(flagged.returncode, 0)
        self.assertIn("R15", flagged.stdout)
        cited = GOOD_REPORT.replace(marker, marker + "\nBoth trials show a positive effect [S1, S2].\n")
        self.assertClean(self.report(cited, "--strict"))

    def test_uncited_figure_in_findings(self):
        heading = "### 2. The improvement may not last [C2]"
        result = self.report(GOOD_REPORT.replace(heading, heading + "\n\nAttendance rose by 14% in the same period."))
        self.assertIn("R16", result.stdout)
        self.assertIn("'14%'", result.stdout)

    def test_dropped_finding_and_source_are_noticed(self):
        start, end = GOOD_REPORT.index("### 3."), GOOD_REPORT.index("## Where the evidence disagrees")
        cut = (GOOD_REPORT[:start] + GOOD_REPORT[end:]).replace("makes plausible [S4]", "makes plausible")
        result = self.report(cut)
        self.assertIn("R12 C3", result.stdout)
        self.assertIn("R13 S4", result.stdout)

    def test_code_blocks_are_not_read_as_prose(self):
        self.assertClean(self.report(GOOD_REPORT + "\n```\nTODO [S99] studies show\n```\n", "--strict"))

    def test_report_cannot_be_final_with_unconfirmed_evidence(self):
        del self.claims["C1"]["support"][0]["checked"]
        result = self.report(GOOD_REPORT)
        self.assertEqual(result.returncode, 1)
        self.assertIn("V04", result.stdout)
        self.ledger["mode"] = "rapid"
        self.assertNotIn("V04", self.report(GOOD_REPORT).stdout)

    def test_unreadable_report(self):
        self.assertEqual(tool("report", str(self.dir / "absent.md"), self.save()).returncode, 2)
        self.assertEqual(self.report("  \n").returncode, 2)


class Views(Case):
    def test_tables(self):
        result = tool("tables", self.save())
        self.assertEqual(result.returncode, 0, result.stderr)
        for heading in ("### Flow", "### Exclusions by reason", "### Search log", "### Included sources",
                        "### Excluded sources", "### Claims", "### Evidence matrix"):
            self.assertIn(heading, result.stdout)
        self.assertIn("| Independent lineages | 5 |", result.stdout)
        self.assertIn("| C1 | + | + | + |  | - |", result.stdout)

    def test_tables_to_file_and_pipe_escaping(self):
        self.sources["S1"]["title"] = "A | B"
        out = self.dir / "tables.md"
        self.assertEqual(tool("tables", self.save(), "-o", str(out)).returncode, 0)
        self.assertIn("A \\| B", out.read_text(encoding="utf-8"))

    def test_trace_follows_a_recommendation_to_its_sources(self):
        result = tool("trace", self.save(), "C4")
        self.assertEqual(result.returncode, 0)
        for expected in ("C4 [recommendation]", "based on:", "C1 [finding]", "supported by S1 at Table 4, p. 31",
                         "contradicted by S5", "reconciled:"):
            self.assertIn(expected, result.stdout)

    def test_views_cope_with_an_empty_ledger(self):
        path = self.save({"question": "q"})
        for command in ("ceilings", "keystones", "worksheet", "trace", "tables"):
            result = tool(command, path)
            self.assertEqual(result.returncode, 0, command + result.stderr)

    def test_explain(self):
        self.assertIn("C01 (error): Certainty exceeds what the evidence can carry", tool("explain", "c01").stdout)
        self.assertEqual(tool("explain", "Z99").returncode, 2)


class ShippedMaterial(unittest.TestCase):
    def test_rule_table_in_the_reference_matches_the_code(self):
        documented = (SKILL / "references" / "evidence-ledger.md").read_text(encoding="utf-8")
        for line in tool("explain").stdout.strip().splitlines():
            self.assertIn(line, documented)

    def test_worked_example_passes_its_own_checks(self):
        ledger, report = str(EXAMPLE / "ledger.json"), str(EXAMPLE / "report.md")
        for result in (tool("check", ledger, "--strict"), tool("report", report, ledger, "--strict")):
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_worked_example_figures_appear_in_the_source_documents(self):
        """Every figure the example ledger records can be found in the file it cites."""
        import re
        data = json.loads((EXAMPLE / "ledger.json").read_text(encoding="utf-8"))
        refs = {s["id"]: ROOT / s["ref"] for s in data["sources"]}
        for claim in data["claims"]:
            for item in claim.get("support", []) + claim.get("contradicts", []):
                if item["kind"] != "data":
                    continue
                source_text = refs[item["source"]].read_text(encoding="utf-8")
                for figure in re.findall(r"-?\d+(?:\.\d+)?%?", item["text"]):
                    self.assertIn(figure.lstrip("-"), source_text, f"{claim['id']} {item['source']} {figure}")


if __name__ == "__main__":
    unittest.main()
