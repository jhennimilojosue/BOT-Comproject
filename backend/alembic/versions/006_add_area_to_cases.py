"""006_add_area_to_cases

Revision ID: 006
Revises: 005
Create Date: 2026-09-07
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column(
            "area",
            sa.String(200),
            nullable=True,
            comment="Área asociada al caso en Aranda",
        ),
    )


def downgrade() -> None:
    op.drop_column("cases", "area")