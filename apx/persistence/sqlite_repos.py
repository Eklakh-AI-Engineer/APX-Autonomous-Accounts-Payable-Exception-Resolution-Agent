from __future__ import annotations

import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, func, update
from sqlalchemy.orm import Session

from apx.persistence.database import session_scope
from apx.persistence.models import (
    InvoiceORM,
    GroundTruthORM,
    CaseORM,
    ApprovalORM,
    ActionORM,
    ActionAttemptORM,
    AuditEventORM,
)
from apx.persistence.repositories import (
    InvoiceRepository,
    CaseRepository,
    ApprovalRepository,
    ActionRepository,
    AuditRepository,
)
from apx.action.models import ApprovalRequest, ApprovalStatus, ActionType, ActionPlan, ActionResult, ActionStatus
from apx.data.schemas import (
    Invoice,
    Vendor,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    GoodsReceiptLine,
    InvoiceLine,
    Currency,
    POStatus,
    GRNStatus,
    ValidationStatus,
    ExceptionCode,
    GroundTruth,
    APException,
    ExceptionSeverity,
)
from apx.agent.models import InvestigationResult, InvestigationStep
from apx.risk.models import RiskAssessment, RiskDimensionScore, RiskDimension, RiskLevel
from apx.guardrail.models import (
    GuardrailDecisionResult,
    ActionType,
    GuardrailDecision,
    GuardrailCheckResult,
    ApprovalStatus,
)
from apx.action.models import ActionPlan, ActionResult, ActionStatus
from apx.evidence.schemas import EvidenceSet, ValidityStatus


class _InvoiceSerializer:
    """Serialization helpers for Invoice domain objects."""

    @staticmethod
    def to_orm(invoice: Invoice, ground_truth: Optional[GroundTruth] = None) -> Tuple[InvoiceORM, Optional[GroundTruthORM]]:
        """Convert domain Invoice to ORM models."""
        # Serialize full invoice to JSON for replay capability
        payload = {
            "invoice_id": invoice.invoice_id,
            "vendor_id": invoice.vendor_id,
            "invoice_number": invoice.invoice_number,
            "po_number": invoice.po_number,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "currency": invoice.currency.value,
            "subtotal": str(invoice.subtotal),
            "tax": str(invoice.tax),
            "total": str(invoice.total),
            "discount": str(invoice.discount),
            "line_items": [
                {
                    "line_id": line.line_id,
                    "description": line.description,
                    "po_line_id": line.po_line_id,
                    "quantity": str(line.quantity),
                    "unit_price": str(line.unit_price),
                    "discount": str(line.discount),
                    "tax_rate": str(line.tax_rate),
                }
                for line in invoice.line_items
            ],
        }

        orm_invoice = InvoiceORM(
            invoice_id=invoice.invoice_id,
            vendor_id=invoice.vendor_id,
            invoice_number=invoice.invoice_number,
            po_number=invoice.po_number,
            invoice_date=invoice.invoice_date,
            due_date=invoice.due_date,
            currency=invoice.currency.value,
            subtotal=invoice.subtotal,
            tax=invoice.tax,
            total=invoice.total,
            discount=invoice.discount,
            payload_json=payload,
        )

        orm_ground_truth = None
        if ground_truth:
            orm_ground_truth = GroundTruthORM(
                invoice_id=ground_truth.invoice_id,
                expected_exceptions=[e.value for e in ground_truth.expected_exceptions],
                expected_decision=ground_truth.expected_decision,
                injected_exceptions=ground_truth.injected_exceptions,
            )

        return orm_invoice, orm_ground_truth

    @staticmethod
    def from_orm(orm: InvoiceORM) -> Invoice:
        """Convert ORM model to domain Invoice."""
        payload = orm.payload_json
        line_items = []
        for line_data in payload.get("line_items", []):
            line_items.append(InvoiceLine(
                line_id=line_data["line_id"],
                description=line_data["description"],
                po_line_id=line_data.get("po_line_id"),
                quantity=Decimal(line_data["quantity"]),
                unit_price=Decimal(line_data["unit_price"]),
                discount=Decimal(line_data["discount"]),
                tax_rate=Decimal(line_data["tax_rate"]),
            ))

        return Invoice(
            invoice_id=orm.invoice_id,
            vendor_id=orm.vendor_id,
            invoice_number=orm.invoice_number,
            po_number=orm.po_number,
            invoice_date=orm.invoice_date,
            due_date=orm.due_date,
            currency=Currency(orm.currency),
            subtotal=orm.subtotal,
            tax=orm.tax,
            total=orm.total,
            discount=orm.discount,
            line_items=line_items,
            created_at=orm.created_at,
        )

    @staticmethod
    def ground_truth_from_orm(orm: GroundTruthORM) -> GroundTruth:
        """Convert ORM ground truth to domain."""
        return GroundTruth(
            invoice_id=orm.invoice_id,
            expected_exceptions=[ExceptionCode(e) for e in orm.expected_exceptions],
            expected_decision=orm.expected_decision,
            injected_exceptions=orm.injected_exceptions,
        )


class _CaseSerializer:
    """Serialization helpers for Case domain objects."""

    @staticmethod
    def investigation_result_to_dict(result: InvestigationResult) -> Dict[str, Any]:
        """Convert InvestigationResult to JSON-serializable dict."""
        return {
            "case_id": result.case_id,
            "invoice_id": result.invoice_id,
            "vendor_id": result.vendor_id,
            "exception_codes": result.exception_codes,
            "final_state": result.final_state.value if hasattr(result.final_state, 'value') else str(result.final_state),
            "outcome": result.outcome.value if result.outcome and hasattr(result.outcome, 'value') else str(result.outcome) if result.outcome else None,
            "evidence_ids": result.evidence_ids,
            "findings": result.findings,
            "steps": [
                {
                    "step_number": step.step_number,
                    "action": step.action,
                    "state_before": step.state_before.value if hasattr(step.state_before, 'value') else str(step.state_before),
                    "state_after": step.state_after.value if hasattr(step.state_after, 'value') else str(step.state_after),
                    "evidence_ids": step.evidence_ids,
                    "finding": step.finding,
                    "timestamp": step.timestamp.isoformat(),
                    "budget_consumed": step.budget_consumed,
                }
                for step in result.steps
            ],
            "budget_limit": result.budget_limit,
            "budget_used": result.budget_used,
            "termination_reason": result.termination_reason,
        }

    @staticmethod
    def risk_assessment_to_dict(assessment: RiskAssessment) -> Dict[str, Any]:
        """Convert RiskAssessment to JSON-serializable dict."""
        return {
            "overall_score": str(assessment.overall_score),
            "risk_level": assessment.risk_level.value if hasattr(assessment.risk_level, 'value') else str(assessment.risk_level),
            "dimension_scores": [
                {
                    "dimension": ds.dimension.value if hasattr(ds.dimension, 'value') else str(ds.dimension),
                    "score": str(ds.score),
                    "weight": str(ds.weight),
                    "weighted_score": str(ds.weighted_score),
                    "factors": ds.factors,
                    "source_evidence_ids": ds.source_evidence_ids,
                }
                for ds in assessment.dimension_scores
            ],
            "investigation_outcome": assessment.investigation_outcome,
            "evidence_ids": assessment.evidence_ids,
            "calculation_metadata": assessment.calculation_metadata,
            "reasons": assessment.reasons,
        }

    @staticmethod
    def guardrail_result_to_dict(result: GuardrailDecisionResult) -> Dict[str, Any]:
        """Convert GuardrailDecisionResult to JSON-serializable dict."""
        return {
            "decision": result.decision.value if hasattr(result.decision, 'value') else str(result.decision),
            "action_type": result.action_type.value if hasattr(result.action_type, 'value') else str(result.action_type),
            "checks": [
                {
                    "check_name": c.check_name,
                    "passed": c.passed,
                    "reason": c.reason,
                    "severity": c.severity,
                }
                for c in result.checks
            ],
            "risk_level": result.risk_level,
            "requires_approval": result.requires_approval,
            "approval_status": result.approval_status.value if hasattr(result.approval_status, 'value') else str(result.approval_status),
            "approval_reason": result.approval_reason,
            "idempotency_key": result.idempotency_key,
            "rate_limit_ok": result.rate_limit_ok,
            "rate_limit_reason": result.rate_limit_reason,
            "block_reason": result.block_reason,
            "allowed_action_types": [a.value if hasattr(a, 'value') else str(a) for a in result.allowed_action_types],
            "required_approvals": result.required_approvals,
            "metadata": result.metadata,
        }

    @staticmethod
    def action_plan_to_dict(plan: ActionPlan) -> Dict[str, Any]:
        """Convert ActionPlan to JSON-serializable dict."""
        return {
            "action_id": plan.action_id,
            "exception_id": plan.exception_id,
            "action_type": plan.action_type.value if hasattr(plan.action_type, 'value') else str(plan.action_type),
            "target": plan.target,
            "parameters": plan.parameters,
            "approval_status": plan.approval_status.value if hasattr(plan.approval_status, 'value') else str(plan.approval_status),
            "idempotency_key": plan.idempotency_key,
            "rate_limit_ok": plan.rate_limit_ok,
            "evidence_ids": plan.evidence_ids,
            "investigation_result_ref": plan.investigation_result_ref,
            "investigation_outcome": plan.investigation_outcome,
            "status": plan.status.value if hasattr(plan.status, 'value') else str(plan.status),
            "created_at": plan.created_at.isoformat() if plan.created_at else None,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
        }


class SQLiteInvoiceRepository(InvoiceRepository):
    """SQLite implementation of InvoiceRepository."""

    def create(self, invoice: Invoice, ground_truth: Optional[GroundTruth] = None) -> str:
        with session_scope() as session:
            orm_invoice, orm_gt = _InvoiceSerializer.to_orm(invoice, ground_truth)
            session.add(orm_invoice)
            if orm_gt:
                session.add(orm_gt)
            session.flush()
            return orm_invoice.invoice_id

    def get(self, invoice_id: str) -> Optional[Invoice]:
        with session_scope() as session:
            orm = session.get(InvoiceORM, invoice_id)
            if orm:
                return _InvoiceSerializer.from_orm(orm)
            return None

    def get_with_ground_truth(self, invoice_id: str) -> Optional[Tuple[Invoice, Optional[GroundTruth]]]:
        with session_scope() as session:
            orm = session.get(InvoiceORM, invoice_id)
            if not orm:
                return None
            invoice = _InvoiceSerializer.from_orm(orm)
            gt = None
            if orm.ground_truth:
                gt = _InvoiceSerializer.ground_truth_from_orm(orm.ground_truth)
            return invoice, gt

    def exists(self, invoice_id: str) -> bool:
        with session_scope() as session:
            return session.query(select(InvoiceORM.invoice_id).where(InvoiceORM.invoice_id == invoice_id).exists()).scalar()

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Invoice]:
        with session_scope() as session:
            stmt = select(InvoiceORM).order_by(InvoiceORM.created_at.desc()).limit(limit).offset(offset)
            orms = session.execute(stmt).scalars().all()
            return [_InvoiceSerializer.from_orm(orm) for orm in orms]

    def delete(self, invoice_id: str) -> bool:
        with session_scope() as session:
            orm = session.get(InvoiceORM, invoice_id)
            if orm:
                session.delete(orm)
                return True
            return False


class SQLiteCaseRepository(CaseRepository):
    """SQLite implementation of CaseRepository."""

    def create(
        self,
        case_id: UUID,
        invoice_id: str,
        vendor_id: str,
        idempotency_key: Optional[str] = None,
    ) -> UUID:
        with session_scope() as session:
            case = CaseORM(
                case_id=case_id,
                invoice_id=invoice_id,
                vendor_id=vendor_id,
                status="NEW",
                current_phase="phase1",
                idempotency_key=idempotency_key,
            )
            session.add(case)
            session.flush()
            return case.case_id

    def get(self, case_id: UUID) -> Optional[Dict[str, Any]]:
        with session_scope() as session:
            orm = session.get(CaseORM, case_id)
            if orm:
                return self._orm_to_dict(orm)
            return None

    def get_by_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        with session_scope() as session:
            stmt = select(CaseORM).where(CaseORM.invoice_id == invoice_id)
            orm = session.execute(stmt).scalar_one_or_none()
            if orm:
                return self._orm_to_dict(orm)
            return None

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        with session_scope() as session:
            stmt = select(CaseORM).where(CaseORM.idempotency_key == idempotency_key)
            orm = session.execute(stmt).scalar_one_or_none()
            if orm:
                return self._orm_to_dict(orm)
            return None

    def update_status(
        self,
        case_id: UUID,
        status: str,
        current_phase: Optional[str] = None,
        **kwargs,
    ) -> bool:
        with session_scope() as session:
            orm = session.get(CaseORM, case_id)
            if not orm:
                return False
            orm.status = status
            if current_phase:
                orm.current_phase = current_phase
            for key, value in kwargs.items():
                if hasattr(orm, key):
                    setattr(orm, key, value)
            return True

    def update_phase1_result(
        self,
        case_id: UUID,
        exception_codes: List[str],
        validation_status: str,
    ) -> bool:
        with session_scope() as session:
            orm = session.get(CaseORM, case_id)
            if not orm:
                return False
            orm.exception_codes = exception_codes
            orm.validation_status = validation_status
            orm.current_phase = "phase2"
            orm.status = "VALIDATING" if exception_codes else "COMPLETED"
            return True

    def update_phase2_result(
        self,
        case_id: UUID,
        evidence_count: int,
        valid_evidence_count: int,
    ) -> bool:
        with session_scope() as session:
            orm = session.get(CaseORM, case_id)
            if not orm:
                return False
            orm.evidence_count = evidence_count
            orm.valid_evidence_count = valid_evidence_count
            orm.current_phase = "phase3"
            orm.status = "RETRIEVING"
            return True

    def update_phase3_result(
        self,
        case_id: UUID,
        investigation_result: InvestigationResult,
    ) -> bool:
        with session_scope() as session:
            orm = session.get(CaseORM, case_id)
            if not orm:
                return False
            orm.investigation_outcome = (
                investigation_result.outcome.value
                if investigation_result.outcome and hasattr(investigation_result.outcome, 'value')
                else str(investigation_result.outcome) if investigation_result.outcome else None
            )
            orm.investigation_findings = investigation_result.findings
            orm.investigation_budget_limit = investigation_result.budget_limit
            orm.investigation_budget_used = investigation_result.budget_used
            orm.investigation_steps = _CaseSerializer.investigation_result_to_dict(investigation_result).get("steps", [])
            orm.current_phase = "phase4"
            orm.status = "INVESTIGATING"
            return True

    def update_phase4_result(
        self,
        case_id: UUID,
        risk_assessment: RiskAssessment,
        guardrail_result: GuardrailDecisionResult,
        action_plan: ActionPlan,
    ) -> bool:
        with session_scope() as session:
            orm = session.get(CaseORM, case_id)
            if not orm:
                return False
            orm.risk_level = risk_assessment.risk_level.value if hasattr(risk_assessment.risk_level, 'value') else str(risk_assessment.risk_level)
            orm.risk_score = risk_assessment.overall_score
            orm.action_type = action_plan.action_type.value if hasattr(action_plan.action_type, 'value') else str(action_plan.action_type)
            orm.action_status = action_plan.status.value if hasattr(action_plan.status, 'value') else str(action_plan.status)
            orm.guardrail_decision = guardrail_result.decision.value if hasattr(guardrail_result.decision, 'value') else str(guardrail_result.decision)
            orm.guardrail_checks = _CaseSerializer.guardrail_result_to_dict(guardrail_result).get("checks", [])
            orm.current_phase = "phase4"
            orm.status = "DECIDING" if guardrail_result.requires_approval else "APPROVING"
            return True

    def list_all(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        with session_scope() as session:
            stmt = select(CaseORM).order_by(CaseORM.created_at.desc())
            if status:
                stmt = stmt.where(CaseORM.status == status)
            stmt = stmt.limit(limit).offset(offset)
            orms = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(orm) for orm in orms]

    def delete(self, case_id: UUID) -> bool:
        with session_scope() as session:
            orm = session.get(CaseORM, case_id)
            if orm:
                session.delete(orm)
                return True
            return False

    def _orm_to_dict(self, orm: CaseORM) -> Dict[str, Any]:
        return {
            "case_id": str(orm.case_id),
            "invoice_id": orm.invoice_id,
            "vendor_id": orm.vendor_id,
            "status": orm.status,
            "current_phase": orm.current_phase,
            "exception_codes": orm.exception_codes,
            "validation_status": orm.validation_status,
            "evidence_count": orm.evidence_count,
            "valid_evidence_count": orm.valid_evidence_count,
            "risk_level": orm.risk_level,
            "risk_score": str(orm.risk_score) if orm.risk_score else None,
            "investigation_outcome": orm.investigation_outcome,
            "investigation_findings": orm.investigation_findings,
            "investigation_budget_limit": orm.investigation_budget_limit,
            "investigation_budget_used": orm.investigation_budget_used,
            "investigation_steps": orm.investigation_steps,
            "action_type": orm.action_type,
            "action_status": orm.action_status,
            "guardrail_decision": orm.guardrail_decision,
            "guardrail_checks": orm.guardrail_checks,
            "idempotency_key": orm.idempotency_key,
            "created_at": orm.created_at.isoformat() if orm.created_at else None,
            "updated_at": orm.updated_at.isoformat() if orm.updated_at else None,
            "completed_at": orm.completed_at.isoformat() if orm.completed_at else None,
        }


class SQLiteApprovalRepository(ApprovalRepository):
    """SQLite implementation of ApprovalRepository."""

    def create(self, approval: ApprovalRequest) -> UUID:
        with session_scope() as session:
            # Convert ApprovalRequest to ORM
            orm = ApprovalORM(
                approval_id=UUID(approval.approval_id),
                case_id=UUID(approval.action_plan_id) if approval.action_plan_id else None,
                action_type=approval.action_type,
                risk_level=approval.risk_level,
                status=approval.status.value if hasattr(approval.status, 'value') else str(approval.status),
                required_approvers=approval.required_approvers,
                approvals_json=approval.approvals,
                requested_by=approval.requested_by,
                resolved_by=approval.resolved_by or None,
                resolved_at=approval.resolved_at,
                action_fingerprint=approval.action_fingerprint,
                evidence_digest=approval.evidence_digest,
                policy_fingerprint=approval.policy_fingerprint,
                requested_at=approval.requested_at,
                expires_at=approval.expires_at,
                revoked_at=approval.revoked_at,
                notes=approval.resolution_notes if approval.resolution_notes else "",
            )
            session.add(orm)
            session.flush()
            return orm.approval_id

    def get(self, approval_id: UUID) -> Optional[ApprovalRequest]:
        with session_scope() as session:
            orm = session.get(ApprovalORM, approval_id)
            if orm:
                return self._orm_to_domain(orm)
            return None

    def get_by_case(self, case_id: UUID) -> Optional[ApprovalRequest]:
        with session_scope() as session:
            stmt = select(ApprovalORM).where(ApprovalORM.case_id == case_id)
            orm = session.execute(stmt).scalar_one_or_none()
            if orm:
                return self._orm_to_domain(orm)
            return None

    def update_status(
        self,
        approval_id: UUID,
        status: ApprovalStatus,
        approver_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> bool:
        with session_scope() as session:
            orm = session.get(ApprovalORM, approval_id)
            if not orm:
                return False
            status_str = status.value if hasattr(status, 'value') else str(status)
            orm.status = status_str
            if approver_id:
                orm.resolved_by = approver_id
            orm.resolved_at = datetime.utcnow()
            if notes:
                orm.notes = notes
            return True

    def add_approval(
        self,
        approval_id: UUID,
        approver_id: str,
        approved: bool,
        notes: Optional[str] = None,
    ) -> bool:
        with session_scope() as session:
            orm = session.get(ApprovalORM, approval_id)
            if not orm:
                return False
            approvals = dict(orm.approvals_json) if orm.approvals_json else {}
            approvals[approver_id] = {
                "approved": approved,
                "notes": notes,
                "timestamp": datetime.utcnow().isoformat(),
            }
            orm.approvals_json = approvals
            return True

    def resolve(
        self, approval_id: UUID, status: ApprovalStatus, approver_id: str,
        notes: Optional[str] = None,
    ) -> bool:
        """Claim the pending approval and record its decision in one transaction."""
        if status not in (ApprovalStatus.APPROVED, ApprovalStatus.REJECTED):
            raise ValueError("Approval resolution must be APPROVED or REJECTED")
        now = datetime.utcnow()
        with session_scope() as session:
            claimed = session.execute(
                update(ApprovalORM)
                .where(
                    ApprovalORM.approval_id == approval_id,
                    ApprovalORM.status == ApprovalStatus.PENDING.value,
                    ApprovalORM.revoked_at.is_(None),
                    ApprovalORM.expires_at.is_not(None),
                    ApprovalORM.expires_at > now,
                )
                .values(status=status.value, resolved_by=approver_id, resolved_at=now, notes=notes or "")
            )
            if claimed.rowcount != 1:
                return False
            orm = session.get(ApprovalORM, approval_id)
            approvals = dict(orm.approvals_json) if orm.approvals_json else {}
            approvals[approver_id] = {
                "approved": status == ApprovalStatus.APPROVED,
                "notes": notes,
                "timestamp": now.isoformat(),
            }
            orm.approvals_json = approvals
            return True

    def revoke(self, approval_id: UUID, actor_id: str, notes: Optional[str] = None) -> bool:
        """Atomically revoke an unresolved or approved grant; identity is retained."""
        now = datetime.utcnow()
        with session_scope() as session:
            result = session.execute(update(ApprovalORM).where(
                ApprovalORM.approval_id == approval_id,
                ApprovalORM.status.in_(("PENDING", "APPROVED")),
                ApprovalORM.revoked_at.is_(None),
            ).values(revoked_at=now, status="REJECTED", resolved_by=actor_id,
                     resolved_at=now, notes=notes or "Revoked"))
            return result.rowcount == 1

    def list_pending(self, limit: int = 100, offset: int = 0) -> List[ApprovalRequest]:
        with session_scope() as session:
            stmt = select(ApprovalORM).where(ApprovalORM.status == "PENDING").order_by(ApprovalORM.requested_at.desc()).limit(limit).offset(offset)
            orms = session.execute(stmt).scalars().all()
            return [self._orm_to_domain(orm) for orm in orms]

    def list_all(self, limit: int = 100, offset: int = 0) -> List[ApprovalRequest]:
        with session_scope() as session:
            stmt = select(ApprovalORM).order_by(ApprovalORM.requested_at.desc()).limit(limit).offset(offset)
            orms = session.execute(stmt).scalars().all()
            return [self._orm_to_domain(orm) for orm in orms]

    def delete(self, approval_id: UUID) -> bool:
        with session_scope() as session:
            orm = session.get(ApprovalORM, approval_id)
            if orm:
                session.delete(orm)
                return True
            return False

    def _orm_to_domain(self, orm: ApprovalORM) -> ApprovalRequest:
        # Extract just the boolean approval values for the domain model
        approvals_bool = {}
        if orm.approvals_json:
            for k, v in orm.approvals_json.items():
                if isinstance(v, dict) and "approved" in v:
                    approvals_bool[k] = v["approved"]
                elif isinstance(v, bool):
                    approvals_bool[k] = v
        
        return ApprovalRequest(
            approval_id=str(orm.approval_id),
            action_plan_id=str(orm.case_id),
            action_type=orm.action_type,
            risk_level=orm.risk_level,
            requested_by=orm.requested_by,
            action_fingerprint=orm.action_fingerprint or "",
            evidence_digest=orm.evidence_digest or "",
            policy_fingerprint=orm.policy_fingerprint or "",
            status=ApprovalStatus(orm.status),
            required_approvers=orm.required_approvers,
            approvals=approvals_bool,
            requested_at=orm.requested_at,
            resolved_by=orm.resolved_by or "",
            resolved_at=orm.resolved_at,
            expires_at=orm.expires_at,
            revoked_at=orm.revoked_at,
            resolution_notes=orm.notes,
        )


class SQLiteActionRepository(ActionRepository):
    """SQLite implementation of ActionRepository."""

    def create(self, action_plan: ActionPlan) -> UUID:
        from apx.action.integrity import action_fingerprint

        metadata = action_plan.metadata or {}
        case_value = metadata.get("case_id") or action_plan.exception_id
        if not case_value:
            raise ValueError("Durable action requires a case_id")
        case_id = UUID(str(case_value))
        evidence_digest = str(metadata.get("evidence_digest") or "")
        policy_fingerprint = str(metadata.get("policy_fingerprint") or "")
        # Bind retries/repeated requests to the logical action, not a worker attempt.
        logical_key = str(action_plan.idempotency_key)
        approval_id = metadata.get("approval_id")
        fingerprint = action_fingerprint(action_plan, evidence_digest, policy_fingerprint)
        with session_scope() as session:
            existing = session.execute(
                select(ActionORM).where(ActionORM.idempotency_key == logical_key)
            ).scalar_one_or_none()
            if existing:
                if (
                    existing.action_type != getattr(action_plan.action_type, "value", action_plan.action_type)
                    or existing.target != action_plan.target
                    or existing.parameters_json != action_plan.parameters
                    or existing.evidence_digest != evidence_digest
                    or existing.policy_fingerprint != policy_fingerprint
                ):
                    raise ValueError("Idempotency key is already bound to a different action")
                return existing.action_id
            orm = ActionORM(
                action_id=UUID(action_plan.action_id),
                case_id=case_id,
                approval_id=UUID(str(approval_id)) if approval_id else None,
                action_type=action_plan.action_type.value if hasattr(action_plan.action_type, 'value') else str(action_plan.action_type),
                target=action_plan.target,
                parameters_json=action_plan.parameters,
                status=action_plan.status.value if hasattr(action_plan.status, 'value') else str(action_plan.status),
                idempotency_key=logical_key,
                action_fingerprint=fingerprint,
                evidence_digest=evidence_digest,
                policy_fingerprint=policy_fingerprint,
            )
            session.add(orm)
            session.flush()
            return orm.action_id

    def claim_for_dispatch(
        self, action_id: UUID, *, claim_token: str, lease_seconds: int,
        action_fingerprint: str, evidence_digest: str, policy_fingerprint: str,
    ) -> bool:
        """Atomically claim only a pending action with matching, live approval bindings."""
        from datetime import timedelta
        from types import SimpleNamespace
        from apx.action.integrity import action_fingerprint as compute_action_fingerprint
        now = datetime.utcnow()
        with session_scope() as session:
            action = session.get(ActionORM, action_id)
            if action is None or action.action_fingerprint != action_fingerprint:
                return False
            recomputed = compute_action_fingerprint(SimpleNamespace(
                action_id=str(action.action_id), target=action.target,
                action_type=action.action_type, parameters=action.parameters_json,
                idempotency_key=action.idempotency_key,
            ), evidence_digest, policy_fingerprint)
            if (
                recomputed != action.action_fingerprint
                or action.evidence_digest != evidence_digest
                or action.policy_fingerprint != policy_fingerprint
            ):
                return False
            approval_ok = select(ApprovalORM.approval_id).where(
                ApprovalORM.approval_id == ActionORM.approval_id,
                ApprovalORM.status == "APPROVED", ApprovalORM.revoked_at.is_(None),
                ApprovalORM.expires_at.is_not(None), ApprovalORM.expires_at > now,
                ApprovalORM.resolved_by.is_not(None),
                ApprovalORM.resolved_by != ApprovalORM.requested_by,
                ApprovalORM.action_fingerprint == action_fingerprint,
                ApprovalORM.evidence_digest == evidence_digest,
                ApprovalORM.policy_fingerprint == policy_fingerprint,
            ).exists()
            attempt_number = action.attempt_count + 1
            claimed = session.execute(
                update(ActionORM).where(
                    ActionORM.action_id == action_id,
                    ActionORM.status.in_(("PENDING", "RETRY_WAIT")),
                    (ActionORM.next_retry_at.is_(None) | (ActionORM.next_retry_at <= now)),
                    ActionORM.approval_id.is_not(None), ActionORM.action_fingerprint == action_fingerprint,
                    ActionORM.evidence_digest == evidence_digest,
                    ActionORM.policy_fingerprint == policy_fingerprint, approval_ok,
                ).values(
                    status="DISPATCHING", claim_token=claim_token,
                    lease_expires_at=now + timedelta(seconds=lease_seconds),
                    attempt_count=ActionORM.attempt_count + 1,
                    next_retry_at=None,
                )
            )
            if claimed.rowcount != 1:
                return False
            session.add(ActionAttemptORM(
                action_id=action_id,
                attempt_number=attempt_number,
                claim_token=claim_token, state="INTENT", started_at=now,
            ))
            return True

    def record_dispatch_outcome(
        self, action_id: UUID, claim_token: str, *, state: str,
        downstream_reference: str | None = None, error_code: str | None = None,
    ) -> bool:
        """Persist terminal/uncertain outcome using the current claim as a fencing token."""
        allowed = {"EXECUTED", "FAILED", "OUTCOME_UNKNOWN", "RETRY_WAIT", "DEAD_LETTER"}
        if state not in allowed:
            raise ValueError(f"Unsupported durable action state: {state}")
        now = datetime.utcnow()
        with session_scope() as session:
            changed = session.execute(update(ActionORM).where(
                ActionORM.action_id == action_id, ActionORM.status == "DISPATCHING",
                ActionORM.claim_token == claim_token,
            ).values(
                status=state, downstream_reference=downstream_reference,
                dead_lettered_at=now if state == "DEAD_LETTER" else None,
                error_message=error_code, lease_expires_at=None, claim_token=None,
                next_retry_at=None,
                executed_at=now if state == "EXECUTED" else None,
                result_json={"downstream_reference": downstream_reference} if state == "EXECUTED" else None,
            ))
            if changed.rowcount != 1:
                return False
            attempt = session.execute(select(ActionAttemptORM).where(
                ActionAttemptORM.action_id == action_id,
                ActionAttemptORM.claim_token == claim_token,
            )).scalar_one()
            attempt.state = state
            attempt.finished_at = now
            attempt.downstream_reference = downstream_reference
            attempt.error_code = error_code
            return True

    def verify_claim_for_dispatch(
        self, action_id: UUID, claim_token: str, *,
        action_fingerprint: str, evidence_digest: str, policy_fingerprint: str,
    ) -> bool:
        """Recheck the fence and authorization at the adapter boundary."""
        from types import SimpleNamespace
        from apx.action.integrity import action_fingerprint as compute_action_fingerprint
        now = datetime.utcnow()
        with session_scope() as session:
            action = session.get(ActionORM, action_id)
            if (
                action is None or action.status != "DISPATCHING"
                or action.claim_token != claim_token or action.lease_expires_at is None
                or action.lease_expires_at <= now
            ):
                return False
            recalculated = compute_action_fingerprint(SimpleNamespace(
                action_id=str(action.action_id), target=action.target,
                action_type=action.action_type, parameters=action.parameters_json,
                idempotency_key=action.idempotency_key,
            ), evidence_digest, policy_fingerprint)
            if (
                recalculated != action_fingerprint or action.action_fingerprint != action_fingerprint
                or action.evidence_digest != evidence_digest or action.policy_fingerprint != policy_fingerprint
            ):
                return False
            approval = session.get(ApprovalORM, action.approval_id) if action.approval_id else None
            return bool(
                approval and approval.status == "APPROVED" and approval.revoked_at is None
                and approval.expires_at is not None and approval.expires_at > now
                and approval.resolved_by and approval.resolved_by != approval.requested_by
                and approval.action_fingerprint == action_fingerprint
                and approval.evidence_digest == evidence_digest
                and approval.policy_fingerprint == policy_fingerprint
            )

    def recover_expired_claims(self) -> int:
        """Fence crashed dispatchers into uncertainty; never make them retryable."""
        now = datetime.utcnow()
        with session_scope() as session:
            stale = session.execute(select(ActionORM.action_id, ActionORM.claim_token).where(
                ActionORM.status == "DISPATCHING", ActionORM.lease_expires_at < now,
            )).all()
            for action_id, token in stale:
                session.execute(update(ActionORM).where(
                    ActionORM.action_id == action_id, ActionORM.status == "DISPATCHING",
                    ActionORM.claim_token == token,
                ).values(status="OUTCOME_UNKNOWN", claim_token=None, lease_expires_at=None))
                if token:
                    session.execute(update(ActionAttemptORM).where(
                        ActionAttemptORM.action_id == action_id,
                        ActionAttemptORM.claim_token == token,
                        ActionAttemptORM.state == "INTENT",
                    ).values(state="OUTCOME_UNKNOWN", finished_at=now, error_code="LEASE_EXPIRED"))
            return len(stale)

    def reconcile_outcome(self, action_id: UUID, *, downstream_found: bool, reference: str | None = None) -> bool:
        """Resolve uncertainty from an authoritative downstream lookup before any retry."""
        with session_scope() as session:
            target = "EXECUTED" if downstream_found else "RETRY_WAIT"
            result = session.execute(update(ActionORM).where(
                ActionORM.action_id == action_id, ActionORM.status == "OUTCOME_UNKNOWN",
            ).values(
                status=target, downstream_reference=reference if downstream_found else None,
                executed_at=datetime.utcnow() if downstream_found else None,
                result_json={"downstream_reference": reference} if downstream_found else None,
            ))
            return result.rowcount == 1

    def schedule_retry(self, action_id: UUID, retry_at: datetime) -> bool:
        """Set a durable retry time only after an authoritative no-effect reconciliation."""
        with session_scope() as session:
            result = session.execute(update(ActionORM).where(
                ActionORM.action_id == action_id, ActionORM.status == "RETRY_WAIT",
            ).values(next_retry_at=retry_at))
            return result.rowcount == 1

    def list_dead_letters(self, limit: int = 100) -> List[Dict[str, Any]]:
        with session_scope() as session:
            rows = session.execute(select(ActionORM).where(
                ActionORM.status == "DEAD_LETTER"
            ).order_by(ActionORM.dead_lettered_at.desc()).limit(limit)).scalars().all()
            return [self._orm_to_dict(row) for row in rows]

    def list_attempts(self, action_id: UUID) -> List[Dict[str, Any]]:
        with session_scope() as session:
            rows = session.execute(select(ActionAttemptORM).where(
                ActionAttemptORM.action_id == action_id,
            ).order_by(ActionAttemptORM.attempt_number)).scalars().all()
            return [{
                "attempt_number": row.attempt_number, "state": row.state,
                "claim_token": row.claim_token, "started_at": row.started_at.isoformat(),
                "finished_at": row.finished_at.isoformat() if row.finished_at else None,
                "downstream_reference": row.downstream_reference, "error_code": row.error_code,
            } for row in rows]

    def get(self, action_id: UUID) -> Optional[Dict[str, Any]]:
        with session_scope() as session:
            orm = session.get(ActionORM, action_id)
            if orm:
                return self._orm_to_dict(orm)
            return None

    def get_by_case(self, case_id: UUID) -> Optional[Dict[str, Any]]:
        with session_scope() as session:
            stmt = select(ActionORM).where(ActionORM.case_id == case_id)
            orm = session.execute(stmt).scalar_one_or_none()
            if orm:
                return self._orm_to_dict(orm)
            return None

    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        with session_scope() as session:
            stmt = select(ActionORM).where(ActionORM.idempotency_key == idempotency_key)
            orm = session.execute(stmt).scalar_one_or_none()
            if orm:
                return self._orm_to_dict(orm)
            return None

    def update_execution(
        self,
        action_id: UUID,
        status: str,
        result: Optional[ActionResult] = None,
        error_message: Optional[str] = None,
        retry_count: Optional[int] = None,
    ) -> bool:
        with session_scope() as session:
            orm = session.get(ActionORM, action_id)
            if not orm:
                return False
            orm.status = status
            if result:
                orm.result_json = result.result_data
                orm.executed_at = result.executed_at
            if error_message:
                orm.error_message = error_message
            if retry_count is not None:
                orm.retry_count = retry_count
            return True

    def update_compensation(
        self,
        action_id: UUID,
        compensation_result: Dict[str, Any],
    ) -> bool:
        with session_scope() as session:
            orm = session.get(ActionORM, action_id)
            if not orm:
                return False
            result = orm.result_json or {}
            result["compensation"] = compensation_result
            orm.result_json = result
            return True

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with session_scope() as session:
            stmt = select(ActionORM).order_by(ActionORM.created_at.desc()).limit(limit).offset(offset)
            orms = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(orm) for orm in orms]

    def delete(self, action_id: UUID) -> bool:
        with session_scope() as session:
            orm = session.get(ActionORM, action_id)
            if orm:
                session.delete(orm)
                return True
            return False

    def _orm_to_dict(self, orm: ActionORM) -> Dict[str, Any]:
        return {
            "action_id": str(orm.action_id),
            "case_id": str(orm.case_id),
            "approval_id": str(orm.approval_id) if orm.approval_id else None,
            "action_type": orm.action_type,
            "target": orm.target,
            "parameters": orm.parameters_json,
            "risk_score": str(orm.risk_score) if orm.risk_score else None,
            "guardrail_decision": orm.guardrail_decision,
            "guardrail_checks": orm.guardrail_checks,
            "status": orm.status,
            "idempotency_key": orm.idempotency_key,
            "retry_count": orm.retry_count,
            "attempt_count": orm.attempt_count,
            "action_fingerprint": orm.action_fingerprint,
            "evidence_digest": orm.evidence_digest,
            "policy_fingerprint": orm.policy_fingerprint,
            "lease_expires_at": orm.lease_expires_at.isoformat() if orm.lease_expires_at else None,
            "downstream_reference": orm.downstream_reference,
            "dead_lettered_at": orm.dead_lettered_at.isoformat() if orm.dead_lettered_at else None,
            "result": orm.result_json,
            "error_message": orm.error_message,
            "executed_at": orm.executed_at.isoformat() if orm.executed_at else None,
            "created_at": orm.created_at.isoformat() if orm.created_at else None,
            "updated_at": orm.updated_at.isoformat() if orm.updated_at else None,
        }


class SQLiteAuditRepository(AuditRepository):
    """SQLite implementation of AuditRepository."""

    def log(
        self,
        case_id: UUID,
        event_type: str,
        phase: str,
        component: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> UUID:
        with session_scope() as session:
            event = AuditEventORM(
                case_id=case_id,
                event_type=event_type,
                phase=phase,
                component=component,
                payload_json=payload,
                metadata_json=metadata or {},
                request_id=request_id,
                correlation_id=correlation_id,
                user_id=user_id,
                duration_ms=duration_ms,
            )
            session.add(event)
            session.flush()
            return event.event_id

    def get_by_case(
        self,
        case_id: UUID,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        with session_scope() as session:
            stmt = (
                select(AuditEventORM)
                .where(AuditEventORM.case_id == case_id)
                .order_by(AuditEventORM.created_at.asc())
                .limit(limit)
                .offset(offset)
            )
            orms = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(orm) for orm in orms]

    def get_by_type(
        self,
        event_type: str,
        since: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        with session_scope() as session:
            stmt = select(AuditEventORM).where(AuditEventORM.event_type == event_type)
            if since:
                stmt = stmt.where(AuditEventORM.created_at >= since)
            stmt = stmt.order_by(AuditEventORM.created_at.desc()).limit(limit).offset(offset)
            orms = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(orm) for orm in orms]

    def list_all(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        with session_scope() as session:
            stmt = select(AuditEventORM).order_by(AuditEventORM.created_at.desc()).limit(limit).offset(offset)
            orms = session.execute(stmt).scalars().all()
            return [self._orm_to_dict(orm) for orm in orms]

    def _orm_to_dict(self, orm: AuditEventORM) -> Dict[str, Any]:
        return {
            "event_id": str(orm.event_id),
            "case_id": str(orm.case_id),
            "event_type": orm.event_type,
            "phase": orm.phase,
            "component": orm.component,
            "payload": orm.payload_json,
            "metadata": orm.metadata_json,
            "request_id": orm.request_id,
            "correlation_id": orm.correlation_id,
            "user_id": orm.user_id,
            "duration_ms": orm.duration_ms,
            "created_at": orm.created_at.isoformat() if orm.created_at else None,
        }
