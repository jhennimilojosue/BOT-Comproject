"""007_add_fecha_solucion_to_cases

Revision ID: 007
Revises: 006
Create Date: 2026-09-08
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "cases",
        sa.Column(
            "fecha_solucion",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Fecha de solución del caso en el sistema origen",
        ),
    )


def downgrade() -> None:
    op.drop_column("cases", "fecha_solucion")