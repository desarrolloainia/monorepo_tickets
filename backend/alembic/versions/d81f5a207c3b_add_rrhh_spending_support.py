"""add rrhh spending support

Revision ID: d81f5a207c3b
Revises: c4dc7c2dd890
Create Date: 2026-08-04
"""

from collections.abc import Sequence

from alembic import op

revision: str = "d81f5a207c3b"
down_revision: str | Sequence[str] | None = "c4dc7c2dd890"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.create_check_constraint("ck_users_role", "users", "role IN ('user', 'approver', 'rrhh')")
    op.create_index("ix_issued_tickets_fecha_emision", "issued_tickets", ["fecha_emision"])


def downgrade() -> None:
    op.drop_index("ix_issued_tickets_fecha_emision", table_name="issued_tickets")
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.execute("UPDATE users SET role = 'user' WHERE role = 'rrhh'")
    op.create_check_constraint("ck_users_role", "users", "role IN ('user', 'approver')")
