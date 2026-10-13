from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

from apx.action.models import ActionPlan, ActionResult, ActionType
from apx.guardrail.models import GuardrailDecisionResult, GuardrailDecision
from apx.data.schemas import GroundTruth


@dataclass
class ActionMetrics:
    """Metrics for action evaluation."""
    total_actions: int = 0
    correct_actions: int = 0
    action_accuracy: float = 0.0
    action_evaluation_cases: int = 0
    action_type_correct: int = 0
    action_type_accuracy: float = 0.0
    execution_successes: int = 0
    execution_success_rate: float = 0.0

    # Guardrail metrics
    guardrail_decisions: int = 0
    guardrail_correct: int = 0
    guardrail_accuracy: float = 0.0

    # Safety metrics
    unauthorized_actions: int = 0
    unauthorized_action_rate: float = 0.0

    # Approval metrics
    approvals_required: int = 0
    approvals_correct: int = 0
    approval_accuracy: float = 0.0
    approval_evaluation_cases: int = 0

    # Blocked actions
    blocked_actions: int = 0
    blocked_correct: int = 0
    blocked_expected_positive: int = 0
    blocked_accuracy: float = 0.0
    blocked_precision: float = 0.0
    blocked_recall: float = 0.0
    blocked_predicted_positive: int = 0

    # Escalation metrics
    escalations: int = 0
    escalations_correct: int = 0
    escalation_accuracy: float = 0.0

    # Per-action-type metrics
    per_action_type: Dict[str, Dict[str, int]] = field(default_factory=dict)


@dataclass
class ActionResult:
    """Result of action evaluation."""
    metrics: ActionMetrics = field(default_factory=ActionMetrics)
    per_case: List[Dict[str, Any]] = field(default_factory=list)


class ActionEvaluator:
    """
    Evaluates Phase 4 action/guardrail behavior.

    Measures action correctness, guardrail decision correctness,
    unauthorized-action rate, approval requirement correctness,
    blocked-action correctness, and escalation correctness.
    """

    def __init__(self):
        pass

    _EXPECTED_ACTION_MAP = {
        "AUTO_APPROVE": "AUTO_RESOLVE",
        "REVIEW": "REQUEST_INFORMATION",
        "ESCALATE": "ESCALATE_TO_HUMAN",
    }

    _EXPECTED_GUARDRAIL_DECISIONS = {
        "ESCALATE_TO_HUMAN": {
            "LOW": GuardrailDecision.ALLOW,
            "MEDIUM": GuardrailDecision.ALLOW,
            "HIGH": GuardrailDecision.ALLOW,
            "CRITICAL": GuardrailDecision.ALLOW,
        },
        "MANUAL_REVIEW": {
            "LOW": GuardrailDecision.ALLOW,
            "MEDIUM": GuardrailDecision.ALLOW,
            "HIGH": GuardrailDecision.ALLOW,
            "CRITICAL": GuardrailDecision.ALLOW,
        },
        "REQUEST_INFORMATION": {
            "LOW": GuardrailDecision.ALLOW,
            "MEDIUM": GuardrailDecision.ALLOW,
            "HIGH": GuardrailDecision.ALLOW,
            "CRITICAL": GuardrailDecision.BLOCK,
        },
        "CONTACT_VENDOR": {
            "LOW": GuardrailDecision.ALLOW,
            "MEDIUM": GuardrailDecision.ALLOW,
            "HIGH": GuardrailDecision.ALLOW,
            "CRITICAL": GuardrailDecision.BLOCK,
        },
        "AUTO_RESOLVE": {
            "LOW": GuardrailDecision.ALLOW,
            "MEDIUM": GuardrailDecision.BLOCK,
            "HIGH": GuardrailDecision.BLOCK,
            "CRITICAL": GuardrailDecision.BLOCK,
        },
        "UPDATE_RECORDS": {
            "LOW": GuardrailDecision.ALLOW,
            "MEDIUM": GuardrailDecision.ALLOW,
            "HIGH": GuardrailDecision.BLOCK,
            "CRITICAL": GuardrailDecision.BLOCK,
        },
        "ADJUST_PAYMENT": {
            "LOW": GuardrailDecision.ALLOW,
            "MEDIUM": GuardrailDecision.ALLOW,
            "HIGH": GuardrailDecision.BLOCK,
            "CRITICAL": GuardrailDecision.BLOCK,
        },
        "VOID_INVOICE": {
            "LOW": GuardrailDecision.ALLOW,
            "MEDIUM": GuardrailDecision.ALLOW,
            "HIGH": GuardrailDecision.BLOCK,
            "CRITICAL": GuardrailDecision.BLOCK,
        },
    }

    _APPROVAL_THRESHOLDS = {
        "AUTO_RESOLVE": "LOW",
        "REQUEST_INFORMATION": "HIGH",
        "ESCALATE_TO_HUMAN": "LOW",
        "MANUAL_REVIEW": "LOW",
        "ADJUST_PAYMENT": "LOW",
        "VOID_INVOICE": "LOW",
        "CONTACT_VENDOR": "MEDIUM",
        "UPDATE_RECORDS": "LOW",
    }

    _RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

    def _gt_expected_decision(self, ground_truth: Any) -> Optional[str]:
        if ground_truth is None:
            return None
        if isinstance(ground_truth, dict):
            return ground_truth.get("expected_decision")
        return getattr(ground_truth, "expected_decision", None)

    def _expected_action_type(
        self,
        action_plan: ActionPlan,
        ground_truth: Any,
    ) -> Optional[str]:
        expected_decision = self._gt_expected_decision(ground_truth)
        if expected_decision is not None:
            return self._EXPECTED_ACTION_MAP.get(expected_decision)
        return None

    def _expected_requires_approval(self, expected_action: str, risk_level: str) -> bool:
        if risk_level in ("HIGH", "CRITICAL"):
            return True
        threshold = self._APPROVAL_THRESHOLDS.get(expected_action, "MEDIUM")
        return self._RISK_ORDER.get(risk_level, 0) >= self._RISK_ORDER.get(threshold, 0)

    def evaluate_action(
        self,
        action_plan: ActionPlan,
        action_result: Any,  # ActionResult
        guardrail_result: Any,  # GuardrailDecisionResult
        ground_truth: Any,  # GroundTruth - may have expected_action
    ) -> ActionMetrics:
        """Evaluate a single action execution."""
        metrics = ActionMetrics()
        metrics.total_actions = 1

        action_type = action_plan.action_type.value if action_plan.action_type else "UNKNOWN"
        if action_type not in metrics.per_action_type:
            metrics.per_action_type[action_type] = {
                "total": 0, "correct": 0, "unauthorized": 0, "blocked": 0
            }
        metrics.per_action_type[action_type]["total"] += 1

        expected_action = self._expected_action_type(action_plan, ground_truth)
        expected_decision = self._expected_guardrail_decision(action_plan, ground_truth)
        if expected_action is not None:
            metrics.action_evaluation_cases = 1

        risk_level = None
        if action_plan.risk_assessment:
            risk = action_plan.risk_assessment.risk_level
            risk_level = risk.value if hasattr(risk, "value") else str(risk)

        action_success = bool(action_result and action_result.success)
        action_type_correct = action_type == expected_action if expected_action else False
        if action_success:
            metrics.execution_successes += 1
        if expected_action is not None and action_type_correct:
            metrics.action_type_correct += 1
        if action_success and action_type_correct:
            metrics.correct_actions += 1
            metrics.per_action_type[action_type]["correct"] += 1

        # Guardrail decision correctness
        guardrail_decision = guardrail_result.decision if guardrail_result else None
        if expected_decision is not None:
            metrics.guardrail_decisions += 1
            if guardrail_decision == expected_decision:
                metrics.guardrail_correct += 1

        # Unauthorized action check
        # Unauthorized = action executed when guardrail said BLOCK
        if guardrail_decision == GuardrailDecision.BLOCK and action_success:
            metrics.unauthorized_actions += 1
            metrics.per_action_type[action_type]["unauthorized"] += 1
        metrics.unauthorized_action_rate = (
            metrics.unauthorized_actions / metrics.total_actions if metrics.total_actions > 0 else 0.0
        )

        # Approval correctness
        actual_requires_approval = bool(guardrail_result and guardrail_result.requires_approval)
        expected_approval = (
            self._expected_requires_approval(expected_action, risk_level or "LOW")
            if expected_action else None
        )
        if expected_approval is not None:
            metrics.approval_evaluation_cases = 1
            if actual_requires_approval or expected_approval:
                metrics.approvals_required += 1
            if actual_requires_approval == expected_approval:
                metrics.approvals_correct += 1

        # Blocked actions
        if expected_decision == GuardrailDecision.BLOCK:
            metrics.blocked_expected_positive += 1
        if guardrail_decision == GuardrailDecision.BLOCK:
            metrics.blocked_actions += 1
            if expected_decision is not None:
                metrics.blocked_predicted_positive += 1
            metrics.per_action_type[action_type]["blocked"] += 1
            # Blocked is correct if expected was BLOCK
            if expected_decision == GuardrailDecision.BLOCK:
                metrics.blocked_correct += 1

        # Escalation correctness
        if action_type == "ESCALATE_TO_HUMAN":
            metrics.escalations += 1
            if expected_action == "ESCALATE_TO_HUMAN":
                metrics.escalations_correct += 1

        return metrics

    def _expected_guardrail_decision(
        self,
        action_plan: ActionPlan,
        ground_truth: Any,
    ) -> Any:
        """Determine expected guardrail decision from the expected action and risk."""
        from apx.guardrail.models import GuardrailDecision

        expected_action = self._expected_action_type(action_plan, ground_truth)

        if action_plan.risk_assessment:
            risk = action_plan.risk_assessment.risk_level
            risk_level = risk.value if hasattr(risk, "value") else str(risk)
        else:
            risk_level = None

        if risk_level is None or expected_action is None:
            return None

        decisions = self._EXPECTED_GUARDRAIL_DECISIONS.get(expected_action, {})
        return decisions.get(risk_level, GuardrailDecision.ALLOW)

    def evaluate_batch(
        self,
        action_plans: List[Any],
        action_results: List[Any],
        guardrail_results: List[Any],
        ground_truths: List[Any],
    ) -> ActionResult:
        """Evaluate a batch of actions."""
        aggregate = ActionMetrics()
        per_case = []

        for ap, ar, gr, gt in zip(action_plans, action_results, guardrail_results, ground_truths):
            m = self.evaluate_action(ap, ar, gr, gt)

            # Aggregate
            aggregate.total_actions += m.total_actions
            aggregate.correct_actions += m.correct_actions
            aggregate.action_evaluation_cases += m.action_evaluation_cases
            aggregate.action_type_correct += m.action_type_correct
            aggregate.execution_successes += m.execution_successes
            aggregate.guardrail_decisions += m.guardrail_decisions
            aggregate.guardrail_correct += m.guardrail_correct
            aggregate.unauthorized_actions += m.unauthorized_actions
            aggregate.approvals_required += m.approvals_required
            aggregate.approvals_correct += m.approvals_correct
            aggregate.approval_evaluation_cases += m.approval_evaluation_cases
            aggregate.blocked_actions += m.blocked_actions
            aggregate.blocked_correct += m.blocked_correct
            aggregate.blocked_expected_positive += m.blocked_expected_positive
            aggregate.blocked_predicted_positive += m.blocked_predicted_positive
            aggregate.escalations += m.escalations
            aggregate.escalations_correct += m.escalations_correct

            # Merge per-action-type
            for atype, counts in m.per_action_type.items():
                if atype not in aggregate.per_action_type:
                    aggregate.per_action_type[atype] = {"total": 0, "correct": 0, "unauthorized": 0, "blocked": 0}
                for k, v in counts.items():
                    aggregate.per_action_type[atype][k] += v

            expected_decision = self._gt_expected_decision(gt)
            expected_action = self._expected_action_type(ap, gt) if expected_decision else None
            actual_action = ap.action_type.value if ap.action_type else None
            expected_guardrail = (
                self._expected_guardrail_decision(ap, gt) if expected_decision else None
            )
            actual_guardrail = gr.decision if gr else None
            if hasattr(expected_guardrail, "value"):
                expected_guardrail = expected_guardrail.value
            if hasattr(actual_guardrail, "value"):
                actual_guardrail = actual_guardrail.value
            risk_level = None
            if ap.risk_assessment:
                risk = ap.risk_assessment.risk_level
                risk_level = risk.value if hasattr(risk, "value") else str(risk)
            expected_approval = (
                self._expected_requires_approval(expected_action, risk_level or "LOW")
                if expected_action else None
            )
            actual_approval = bool(gr and gr.requires_approval)
            errors = []
            if expected_action is not None and actual_action != expected_action:
                errors.append("action_type_mismatch")
            # Execution reliability is measured separately. Keep the action error
            # union limited to cases with an expected action label.
            if expected_action is not None and (ar is None or not ar.success):
                errors.append("action_not_successful")
            if expected_guardrail is not None and actual_guardrail != expected_guardrail:
                errors.append("guardrail_mismatch")
            if expected_approval is not None and actual_approval != expected_approval:
                errors.append("approval_requirement_mismatch")

            per_case.append({
                "action_id": ap.action_id,
                "invoice_id": ap.exception_id or ap.target,
                "expected_decision": expected_decision,
                "expected_action_type": expected_action,
                "label_status": "labeled" if expected_action is not None else "missing_expected_action_label",
                "action_type": actual_action,
                "action_type_correct": actual_action == expected_action if expected_action else None,
                "expected_guardrail_decision": expected_guardrail,
                "guardrail_decision": actual_guardrail,
                "expected_requires_approval": expected_approval,
                "requires_approval": actual_approval,
                "action_success": ar.success if ar else None,
                "unauthorized": m.unauthorized_actions > 0,
                "correct": m.correct_actions > 0,
                "errors": errors,
            })

        # Compute aggregate rates
        if aggregate.action_evaluation_cases > 0:
            aggregate.action_accuracy = aggregate.correct_actions / aggregate.action_evaluation_cases
            aggregate.action_type_accuracy = (
                aggregate.action_type_correct / aggregate.action_evaluation_cases
            )
        if aggregate.total_actions > 0:
            aggregate.execution_success_rate = aggregate.execution_successes / aggregate.total_actions
            aggregate.unauthorized_action_rate = aggregate.unauthorized_actions / aggregate.total_actions

        if aggregate.guardrail_decisions > 0:
            aggregate.guardrail_accuracy = aggregate.guardrail_correct / aggregate.guardrail_decisions

        if aggregate.approval_evaluation_cases > 0:
            aggregate.approval_accuracy = aggregate.approvals_correct / aggregate.approval_evaluation_cases

        if aggregate.blocked_expected_positive > 0:
            aggregate.blocked_recall = (
                aggregate.blocked_correct / aggregate.blocked_expected_positive
            )
            aggregate.blocked_accuracy = aggregate.blocked_recall
        if aggregate.blocked_predicted_positive > 0:
            # Preserve the explicitly named predicted-positive denominator.
            aggregate.blocked_precision = (
                aggregate.blocked_correct / aggregate.blocked_predicted_positive
            )

        if aggregate.escalations > 0:
            aggregate.escalation_accuracy = aggregate.escalations_correct / aggregate.escalations

        return ActionResult(metrics=aggregate, per_case=per_case)

    def evaluate_from_phase4_pipeline(
        self,
        pipeline_results: List[Dict[str, Any]],
        ground_truths: Optional[List[Any]] = None,
    ) -> ActionResult:
        """Evaluate using Phase 4 pipeline outputs."""
        action_plans = [r.get("action_plan") for r in pipeline_results]
        action_results = [r.get("action_result") for r in pipeline_results]
        guardrail_results = [r.get("guardrail_result") for r in pipeline_results]
        gt_map = {gt.invoice_id: gt for gt in (ground_truths or [])}
        ground_truths = [gt_map.get(r.get("invoice_id")) for r in pipeline_results]

        return self.evaluate_batch(action_plans, action_results, guardrail_results, ground_truths)
