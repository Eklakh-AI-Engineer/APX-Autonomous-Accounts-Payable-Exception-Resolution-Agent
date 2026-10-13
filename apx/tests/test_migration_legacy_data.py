"""Upgrade a populated legacy schema through the durable dispatch migration."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


MIGRATIONS = Path(__file__).parents[1] / "persistence" / "migrations" / "versions"


def _run_revision(connection, filename):
    spec = spec_from_file_location(f"migration_{filename[:3]}", MIGRATIONS / filename)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    with Operations.context(MigrationContext.configure(connection)):
        module.upgrade()


def test_durable_dispatch_migration_preserves_legacy_records(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    with engine.begin() as connection:
        _run_revision(connection, "001_initial.py")
        connection.execute(text("""
            INSERT INTO invoices (invoice_id, vendor_id, invoice_number, invoice_date,
                due_date, currency, subtotal, tax, total, discount, payload_json)
            VALUES ('INV-LEGACY', 'V-1', 'N-1', '2026-01-01', '2026-02-01',
                'USD', 125, 0, 125, 0, '{}')
        """))
        connection.execute(text("""
            INSERT INTO cases (case_id, invoice_id, vendor_id, status, exception_codes,
                investigation_steps, guardrail_checks)
            VALUES ('00000000-0000-0000-0000-000000000001', 'INV-LEGACY', 'V-1',
                'NEW', '[]', '[]', '[]')
        """))
        connection.execute(text("""
            INSERT INTO approvals (approval_id, case_id, action_type, risk_level, status,
                required_approvers, approvals_json, requested_by, resolved_by)
            VALUES ('00000000-0000-0000-0000-000000000003',
                '00000000-0000-0000-0000-000000000001', 'MANUAL_REVIEW', 'MEDIUM',
                'APPROVED', '["finance"]', '{"finance":"reviewer-1"}',
                'requester-1', 'reviewer-1')
        """))
        connection.execute(text("""
            INSERT INTO actions (action_id, case_id, approval_id, action_type, target,
                parameters_json, guardrail_checks, status)
            VALUES ('00000000-0000-0000-0000-000000000002',
                '00000000-0000-0000-0000-000000000001',
                '00000000-0000-0000-0000-000000000003', 'MANUAL_REVIEW', 'INV-LEGACY',
                '{}', '[]', 'PENDING')
        """))

        _run_revision(connection, "002_approval_integrity.py")
        _run_revision(connection, "003_durable_action_dispatch.py")

        assert connection.execute(text(
            "SELECT invoice_id FROM invoices WHERE invoice_id='INV-LEGACY'"
        )).scalar_one() == "INV-LEGACY"
        legacy_action = connection.execute(text(
            "SELECT status, action_fingerprint, attempt_count FROM actions "
            "WHERE action_id='00000000-0000-0000-0000-000000000002'"
        )).one()
        assert tuple(legacy_action) == ("PENDING", "", 0)
        assert connection.execute(text("SELECT count(*) FROM action_attempts")).scalar_one() == 0
        legacy_approval = connection.execute(text("""
            SELECT status, requested_by, resolved_by, action_fingerprint,
                evidence_digest, policy_fingerprint, expires_at, revoked_at
            FROM approvals
            WHERE approval_id='00000000-0000-0000-0000-000000000003'
        """)).one()
        assert tuple(legacy_approval) == (
            "APPROVED", "requester-1", "reviewer-1", "", "", "", None, None
        )
        assert connection.execute(text(
            "SELECT approval_id FROM actions "
            "WHERE action_id='00000000-0000-0000-0000-000000000002'"
        )).scalar_one() == "00000000-0000-0000-0000-000000000003"

        columns = {col["name"] for col in inspect(connection).get_columns("actions")}
        assert {"action_fingerprint", "claim_token", "lease_expires_at",
                "attempt_count", "downstream_reference", "next_retry_at",
                "dead_lettered_at"} <= columns
    engine.dispose()
