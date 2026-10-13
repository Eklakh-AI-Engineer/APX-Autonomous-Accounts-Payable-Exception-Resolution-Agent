"""Add integrity and lifecycle fields to approval records."""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("approvals", sa.Column("action_fingerprint", sa.String(64), nullable=False, server_default=""))
    op.add_column("approvals", sa.Column("evidence_digest", sa.String(64), nullable=False, server_default=""))
    op.add_column("approvals", sa.Column("policy_fingerprint", sa.String(64), nullable=False, server_default=""))
    op.add_column("approvals", sa.Column("expires_at", sa.DateTime(), nullable=True))
    op.add_column("approvals", sa.Column("revoked_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("approvals", "revoked_at")
    op.drop_column("approvals", "expires_at")
    op.drop_column("approvals", "policy_fingerprint")
    op.drop_column("approvals", "evidence_digest")
    op.drop_column("approvals", "action_fingerprint")
