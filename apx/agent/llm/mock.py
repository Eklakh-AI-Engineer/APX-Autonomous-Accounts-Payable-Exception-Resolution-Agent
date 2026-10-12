from __future__ import annotations

from typing import Any

from apx.agent.llm.base import InvestigationFindings, LLMProvider


class MockLLMProvider(LLMProvider):
    """
    Deterministic mock LLM provider for tests and synthetic DEV benchmarks.

    The synthetic benchmark's decision contract is REVIEW when one or more
    exception codes are present, and AUTO_APPROVE only for a clean report.
    This mock follows that contract so DEV metrics measure the pipeline rather
    than a second, conflicting exception-to-decision heuristic.
    """

    _EXCEPTION_CODES = (
        "AMOUNT_MISMATCH",
        "GRN_MISMATCH",
        "VENDOR_MISMATCH",
        "TAX_ERROR",
        "CREDIT_ISSUE",
        "PO_MISMATCH",
        "CURRENCY_MISMATCH",
        "LINE_ITEM_MISMATCH",
        "DISCOUNT_ERROR",
        "DUPLICATE_INVOICE",
    )

    def __init__(self, seed: int = 42):
        self.seed = seed
        self._call_count = 0

    def get_provider_name(self) -> str:
        return "mock"

    def investigate(
        self,
        exception_report: str,
        evidence_summaries: list[dict],
        current_state: str,
        budget_remaining: int,
    ) -> InvestigationFindings:
        """Return a stable structured decision consistent with the DEV contract."""
        self._call_count += 1

        exception_type = next(
            (code for code in self._EXCEPTION_CODES if code in exception_report),
            None,
        )
        valid_evidence = [
            evidence
            for evidence in evidence_summaries
            if str(evidence.get("validity_status", "")).lower() == "valid"
        ]
        relevant_evidence = [
            evidence
            for evidence in valid_evidence
            if evidence.get("relevance_score", 0) > 0.3
        ]
        evidence_ids = [
            evidence["evidence_id"]
            for evidence in (relevant_evidence or valid_evidence)[:3]
            if evidence.get("evidence_id")
        ]

        if exception_type is None:
            return InvestigationFindings(
                findings="No exception codes were identified; the synthetic case is clean.",
                evidence_ids=evidence_ids,
                proposed_outcome="RESOLVE",
                confidence=0.9,
                information_needed=[],
            )

        return InvestigationFindings(
            findings=(
                f"Identified {exception_type}. The synthetic DEV contract requires "
                "review when an exception is present."
            ),
            evidence_ids=evidence_ids,
            proposed_outcome="REQUEST_INFO",
            confidence=0.8,
            information_needed=["Review exception details and supporting documentation"],
        )

    def get_call_count(self) -> int:
        return self._call_count
