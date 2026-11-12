"""The ledger's vocabulary, and a loaded ledger with the indexes other modules need."""

from __future__ import annotations

import json
import re
from pathlib import Path

MODES = ("rapid", "standard", "systematic")
CORPORA = ("supplied", "searched", "mixed")
SOURCE_TYPES = (
    "systematic-review", "meta-analysis", "primary-study", "report", "dataset",
    "grey-literature", "news", "expert-opinion", "primary-data", "internal",
)
REVIEW_TYPES = ("systematic-review", "meta-analysis")
ACCESS = ("full-text", "abstract-only", "secondary-citation")
STATUSES = ("included", "excluded")
LEVELS = ("very-low", "low", "moderate", "high")  # weakest first
CLAIM_TYPES = ("finding", "interpretation", "recommendation")
DERIVED_TYPES = ("interpretation", "recommendation")
EVIDENCE_KINDS = ("quote", "paraphrase", "data")
CHECK_STATES = ("confirmed", "mismatch")

SOURCE_ID = re.compile(r"^S[A-Z]?\d+$")
CLAIM_ID = re.compile(r"^C\d+$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class LedgerUnreadable(Exception):
    """The file is missing, is not JSON, or is not a JSON object."""


def blank(value) -> bool:
    return value is None or value == [] or (isinstance(value, str) and not value.strip())


def level(name) -> int:
    """Position of a rating on the scale; -1 when it is not a rating."""
    return LEVELS.index(name) if name in LEVELS else -1


def weaker(a: str, b: str) -> str:
    return a if level(a) <= level(b) else b


class Ledger:
    """A parsed ledger. Tolerates malformed content: anything that is not the expected
    shape is skipped here and reported by the structural rules."""

    def __init__(self, data: dict, path: str = "") -> None:
        self.data = data
        self.path = path
        self.protocol = data.get("protocol") if isinstance(data.get("protocol"), dict) else {}
        self.mode = data.get("mode")
        self.raw_sources = data.get("sources") if isinstance(data.get("sources"), list) else []
        self.raw_claims = data.get("claims") if isinstance(data.get("claims"), list) else []
        self.sources: dict[str, dict] = {}
        for src in self.raw_sources:
            if isinstance(src, dict) and isinstance(src.get("id"), str) and src["id"] not in self.sources:
                self.sources[src["id"]] = src
        self.claims: dict[str, dict] = {}
        for claim in self.raw_claims:
            if isinstance(claim, dict) and isinstance(claim.get("id"), str) and claim["id"] not in self.claims:
                self.claims[claim["id"]] = claim

    @classmethod
    def read(cls, path: str) -> "Ledger":
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise LedgerUnreadable(
                f"Cannot find '{path}'. Start one with: python scripts/ledger.py new {path} --question \"...\"")
        except json.JSONDecodeError as exc:
            raise LedgerUnreadable(
                f"'{path}' is not valid JSON (line {exc.lineno}, column {exc.colno}: {exc.msg}).")
        except OSError as exc:
            raise LedgerUnreadable(f"Cannot read '{path}': {exc}.")
        if not isinstance(data, dict):
            raise LedgerUnreadable(
                f"'{path}' must hold one JSON object with question, as_of, mode, protocol, sources and claims.")
        return cls(data, path)

    def write(self, path: str = "") -> None:
        Path(path or self.path).write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Sources -----------------------------------------------------------------

    def included(self) -> dict[str, dict]:
        return {sid: s for sid, s in self.sources.items() if s.get("status") == "included"}

    def is_included(self, sid) -> bool:
        return sid in self.sources and self.sources[sid].get("status") == "included"

    def appraisal(self, sid) -> str:
        appraisal = self.sources.get(sid, {}).get("appraisal")
        return appraisal.get("rating") if isinstance(appraisal, dict) else None

    def lineage(self, sid) -> str:
        return self.sources.get(sid, {}).get("lineage")

    def read_in_full(self, sid) -> bool:
        return self.sources.get(sid, {}).get("access") == "full-text"

    # Evidence ----------------------------------------------------------------

    @staticmethod
    def items(claim: dict, side: str) -> list[dict]:
        """Evidence items on one side of a claim ('support' or 'contradicts')."""
        value = claim.get(side)
        return [i for i in value if isinstance(i, dict)] if isinstance(value, list) else []

    def usable(self, claim: dict, side: str) -> list[dict]:
        """Items whose source exists and is included."""
        return [i for i in self.items(claim, side) if self.is_included(i.get("source"))]

    @staticmethod
    def basis(claim: dict) -> list[str]:
        value = claim.get("based_on")
        return [b for b in value if isinstance(b, str)] if isinstance(value, list) else []

    def cited_sources(self) -> set[str]:
        used: set[str] = set()
        for claim in self.claims.values():
            for side in ("support", "contradicts"):
                used.update(i.get("source") for i in self.usable(claim, side))
        return used

    def address_book(self) -> dict[str, tuple[dict, dict, str]]:
        """Every evidence item by address: C1.s1 is the first supporting item of C1,
        C1.x1 its first contradicting item."""
        book: dict[str, tuple[dict, dict, str]] = {}
        for cid, claim in self.claims.items():
            for side, letter in (("support", "s"), ("contradicts", "x")):
                for n, item in enumerate(self.items(claim, side), start=1):
                    book[f"{cid}.{letter}{n}"] = (claim, item, side)
        return book
