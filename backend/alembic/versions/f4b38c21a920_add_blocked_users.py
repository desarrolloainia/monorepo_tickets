"""add blocked users

Revision ID: f4b38c21a920
Revises: d81f5a207c3b
Create Date: 2026-08-05
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op  # pyright: ignore[reportAttributeAccessIssue]

revision: str = "f4b38c21a920"
down_revision: str | Sequence[str] | None = "d81f5a207c3b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "blocked_users",
        sa.Column("microsoft_oid", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("blocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("microsoft_oid"),
    )


def downgrade() -> None:
    op.drop_table("blocked_users")
