"""Add singleton annual ticket limit, initially unlimited."""
import sqlalchemy as sa
from alembic import op

revision = "b29a13091d22"
down_revision = "a72e91c4d810"
branch_labels = None
depends_on = None


def upgrade() -> None:
    table = op.create_table(
        "ticket_maximums",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cantidad_maxima", sa.Integer(), nullable=True),
        sa.Column("updated_by_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("id = 1", name="ck_ticket_maximum_singleton"),
        sa.CheckConstraint("cantidad_maxima > 0", name="ck_ticket_maximum_positive"),
    )
    op.bulk_insert(table, [{"id": 1}])


def downgrade() -> None:
    op.drop_table("ticket_maximums")
