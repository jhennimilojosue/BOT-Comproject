"""009_add_groups_to_cases

Revision ID: 009
Revises: 008
Create Date: 2026-09-18
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column(
            "groups",
            sa.String(200),
            nullable=True,
            comment="Grupo(s) asociados al caso en Aranda",
        ),
    )
    op.create_index("ix_cases_groups", "cases", ["groups"])


def downgrade() -> None:
    op.drop_index("ix_cases_groups", table_name="cases")
    op.drop_column("cases", "groups")