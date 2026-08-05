"""add accountant role

Revision ID: a72e91c4d810
Revises: f4b38c21a920
Create Date: 2026-08-05
"""

from collections.abc import Sequence

from alembic import op  # pyright: ignore[reportAttributeAccessIssue]

revision: str = "a72e91c4d810"
down_revision: str | Sequence[str] | None = "f4b38c21a920"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('user', 'approver', 'rrhh', 'accountant')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.execute("UPDATE users SET role = 'user' WHERE role = 'accountant'")
    op.create_check_constraint(
        "ck_users_role", "users", "role IN ('user', 'approver', 'rrhh')"
    )
