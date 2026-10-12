from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from decimal import Decimal
import os
import tempfile
from uuid import UUID, uuid4

import pytest
from apx.action.integrity import action_fingerprint
from apx.action.models import ActionPlan, ActionType, ApprovalRequest, ApprovalStatus
from apx.persistence import close_database, init_database, SQLiteActionRepository, SQLiteApprovalRepository, SQLiteCaseRepository
from apx.persistence.database import session_scope
from apx.persistence.models import InvoiceORM


@pytest.fixture
def clean_db():
    close_database()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        path = handle.name
    init_database(database_url=f"sqlite:///{path}", create_tables=True)
    yield
    close_database()
    os.unlink(path)


def _approved_action():
    case_id = uuid4()
    invoice_id = f"INV-{case_id}"
    with session_scope() as session:
        session.add(InvoiceORM(
            invoice_id=invoice_id, vendor_id="V-DURABLE", invoice_number=invoice_id,
            invoice_date=datetime.utcnow().date(), due_date=datetime.utcnow().date(),
            currency="USD", subtotal=Decimal("1"), tax=Decimal("0"), total=Decimal("1"),
            discount=Decimal("0"), payload_json={},
        ))
    SQLiteCaseRepository().create(case_id, invoice_id, "V-DURABLE")
    evidence = "evidence-digest"
    policy = "policy-fingerprint"
    plan = ActionPlan(
        exception_id=str(case_id), action_type=ActionType.MANUAL_REVIEW,
        target=invoice_id, metadata={"case_id": str(case_id), "evidence_digest": evidence,
        "policy_fingerprint": policy},
    )
    fp = action_fingerprint(plan, evidence, policy)
    approval = ApprovalRequest(
        action_plan_id=str(case_id), action_type=plan.action_type.value,
        risk_level="HIGH", requested_by="requester", resolved_by="approver",
        status=ApprovalStatus.APPROVED, action_fingerprint=fp,
        evidence_digest=evidence, policy_fingerprint=policy,
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    approval_id = SQLiteApprovalRepository().create(approval)
    plan.metadata["approval_id"] = str(approval_id)
    action_id = SQLiteActionRepository().create(plan)
    return plan, action_id, fp, evidence, policy


def test_atomic_claim_allows_only_one_worker(clean_db):
    _, action_id, fp, evidence, policy = _approved_action()

    def claim(i):
        return SQLiteActionRepository().claim_for_dispatch(
            action_id, claim_token=f"worker-{i}", lease_seconds=60,
            action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy,
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(claim, (1, 2))) == [False, True]


def test_expired_claim_requires_reconciliation_before_retry(clean_db):
    _, action_id, fp, evidence, policy = _approved_action()
    repo = SQLiteActionRepository()
    assert repo.claim_for_dispatch(action_id, claim_token="crashed", lease_seconds=-1,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy)
    assert repo.recover_expired_claims() == 1
    assert repo.get(action_id)["status"] == "OUTCOME_UNKNOWN"
    assert not repo.claim_for_dispatch(action_id, claim_token="retry-too-soon", lease_seconds=60,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy)
    assert repo.reconcile_outcome(action_id, downstream_found=False)
    assert repo.get(action_id)["status"] == "RETRY_WAIT"
    assert repo.schedule_retry(action_id, datetime.utcnow() + timedelta(hours=1))
    assert not repo.claim_for_dispatch(action_id, claim_token="too-early", lease_seconds=60,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy)


def test_success_reference_and_terminal_attempt_are_durable(clean_db):
    _, action_id, fp, evidence, policy = _approved_action()
    repo = SQLiteActionRepository()
    assert repo.claim_for_dispatch(action_id, claim_token="worker", lease_seconds=60,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy)
    assert repo.record_dispatch_outcome(action_id, "worker", state="EXECUTED",
        downstream_reference="ERP-TXN-42")
    stored = repo.get(action_id)
    assert stored["status"] == "EXECUTED"
    assert stored["downstream_reference"] == "ERP-TXN-42"
    assert repo.list_attempts(action_id)[0]["state"] == "EXECUTED"


def test_crash_after_downstream_success_is_reconciled_without_retry(clean_db):
    _, action_id, fp, evidence, policy = _approved_action()
    repo = SQLiteActionRepository()
    assert repo.claim_for_dispatch(action_id, claim_token="worker", lease_seconds=-1,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy)
    # Simulate provider success followed by a local database outage at success commit.
    import apx.persistence.sqlite_repos as sqlite_repos
    original_scope = sqlite_repos.session_scope
    sqlite_repos.session_scope = lambda: (_ for _ in ()).throw(RuntimeError("injected commit outage"))
    with pytest.raises(RuntimeError, match="commit outage"):
        repo.record_dispatch_outcome(action_id, "worker", state="EXECUTED", downstream_reference="ERP-TXN-43")
    sqlite_repos.session_scope = original_scope
    assert repo.recover_expired_claims() == 1
    assert repo.reconcile_outcome(action_id, downstream_found=True, reference="ERP-TXN-43")
    assert repo.get(action_id)["status"] == "EXECUTED"
    assert repo.get(action_id)["downstream_reference"] == "ERP-TXN-43"


def test_database_failure_does_not_create_a_dispatch_claim(clean_db, monkeypatch):
    _, action_id, fp, evidence, policy = _approved_action()
    import apx.persistence.sqlite_repos as sqlite_repos

    def fail_database():
        raise RuntimeError("injected database outage")

    monkeypatch.setattr(sqlite_repos, "session_scope", fail_database)
    with pytest.raises(RuntimeError, match="database outage"):
        SQLiteActionRepository().claim_for_dispatch(action_id, claim_token="worker", lease_seconds=60,
            action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy)


def test_revoked_approval_fails_closed_at_atomic_claim(clean_db):
    plan, action_id, fp, evidence, policy = _approved_action()
    repo = SQLiteActionRepository()
    approval_id = plan.metadata["approval_id"]
    assert SQLiteApprovalRepository().revoke(UUID(approval_id), "security-admin")
    assert not repo.claim_for_dispatch(action_id, claim_token="worker", lease_seconds=60,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy)


def test_revocation_between_claim_and_adapter_boundary_blocks_dispatch(clean_db):
    plan, action_id, fp, evidence, policy = _approved_action()
    repo = SQLiteActionRepository()
    assert repo.claim_for_dispatch(action_id, claim_token="worker", lease_seconds=60,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy)
    assert SQLiteApprovalRepository().revoke(UUID(plan.metadata["approval_id"]), "security-admin")
    assert not repo.verify_claim_for_dispatch(
        action_id, "worker", action_fingerprint=fp,
        evidence_digest=evidence, policy_fingerprint=policy,
    )


def test_persisted_payload_tampering_fails_closed(clean_db):
    _, action_id, fp, evidence, policy = _approved_action()
    from apx.persistence.database import session_scope
    from apx.persistence.models import ActionORM

    with session_scope() as session:
        action = session.get(ActionORM, action_id)
        action.parameters_json = {"tampered": True}
    assert not SQLiteActionRepository().claim_for_dispatch(
        action_id, claim_token="worker", lease_seconds=60,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy,
    )


def test_expired_approval_fails_closed_at_claim(clean_db):
    plan, action_id, fp, evidence, policy = _approved_action()
    from apx.persistence.database import session_scope
    from apx.persistence.models import ApprovalORM

    with session_scope() as session:
        approval = session.get(ApprovalORM, UUID(plan.metadata["approval_id"]))
        approval.expires_at = datetime.utcnow() - timedelta(seconds=1)
    assert not SQLiteActionRepository().claim_for_dispatch(
        action_id, claim_token="worker", lease_seconds=60,
        action_fingerprint=fp, evidence_digest=evidence, policy_fingerprint=policy,
    )


def test_repeated_creation_returns_same_logical_action(clean_db):
    plan, action_id, _, _, _ = _approved_action()
    repeated = plan.model_copy(deep=True)
    repeated.action_id = str(uuid4())
    import pytest
    with pytest.raises(ValueError, match="different action"):
        repeated.parameters["tampered"] = True
        SQLiteActionRepository().create(repeated)
    repeated.parameters.pop("tampered")
    assert SQLiteActionRepository().create(repeated) == action_id
    assert SQLiteActionRepository().get(action_id) is not None
