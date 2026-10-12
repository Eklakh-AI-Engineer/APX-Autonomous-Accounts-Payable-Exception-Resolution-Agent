"""Add a durable action dispatch lease and attempt journal."""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("actions", sa.Column("action_fingerprint", sa.String(64), nullable=False, server_default=""))
    op.add_column("actions", sa.Column("evidence_digest", sa.String(64), nullable=False, server_default=""))
    op.add_column("actions", sa.Column("policy_fingerprint", sa.String(64), nullable=False, server_default=""))
    op.add_column("actions", sa.Column("claim_token", sa.String(64), nullable=True))
    op.add_column("actions", sa.Column("lease_expires_at", sa.DateTime(), nullable=True))
    op.add_column("actions", sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("actions", sa.Column("downstream_reference", sa.String(256), nullable=True))
    op.add_column("actions", sa.Column("next_retry_at", sa.DateTime(), nullable=True))
    op.add_column("actions", sa.Column("dead_lettered_at", sa.DateTime(), nullable=True))
    op.create_table(
        "action_attempts",
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("action_id", sa.Uuid(), sa.ForeignKey("actions.action_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("claim_token", sa.String(64), nullable=False),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("downstream_reference", sa.String(256), nullable=True),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.PrimaryKeyConstraint("attempt_id"),
        sa.UniqueConstraint("action_id", "attempt_number"),
    )
    op.create_index("ix_action_attempts_action_id", "action_attempts", ["action_id"])


def downgrade() -> None:
    op.drop_index("ix_action_attempts_action_id", table_name="action_attempts")
    op.drop_table("action_attempts")
    for column in (
        "dead_lettered_at", "next_retry_at", "downstream_reference", "attempt_count",
        "lease_expires_at", "claim_token", "policy_fingerprint", "evidence_digest",
        "action_fingerprint",
    ):
        op.drop_column("actions", column)
