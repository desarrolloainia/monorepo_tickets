"""add users and ticket audit

Revision ID: 8a4e3c1b9f02
Revises: 2e7dd6f8d7bc
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "8a4e3c1b9f02"
down_revision: str | Sequence[str] | None = "2e7dd6f8d7bc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("microsoft_oid", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('user', 'approver')", name="ck_users_role"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("microsoft_oid"),
    )
    op.add_column("tickets", sa.Column("created_by_id", sa.Uuid(), nullable=True))
    op.add_column("tickets", sa.Column("approved_by_id", sa.Uuid(), nullable=True))
    op.add_column("tickets", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_tickets_created_by_id", "tickets", ["created_by_id"])
    op.create_foreign_key(
        "fk_tickets_created_by_id_users", "tickets", "users", ["created_by_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_tickets_approved_by_id_users", "tickets", "users", ["approved_by_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_tickets_approved_by_id_users", "tickets", type_="foreignkey")
    op.drop_constraint("fk_tickets_created_by_id_users", "tickets", type_="foreignkey")
    op.drop_index("ix_tickets_created_by_id", table_name="tickets")
    op.drop_column("tickets", "approved_at")
    op.drop_column("tickets", "approved_by_id")
    op.drop_column("tickets", "created_by_id")
    op.drop_table("users")
