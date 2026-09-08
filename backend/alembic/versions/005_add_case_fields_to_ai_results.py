"""005_add_case_fields_to_ai_results

Revision ID: 005
Revises: 004
Create Date: 2026-09-04
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ai_results",
        sa.Column(
            "case_type",
            sa.String(50),
            nullable=True,
            comment="Tipo de caso (Incidente/Requerimiento)",
        ),
    )
    op.add_column(
        "ai_results",
        sa.Column(
            "status",
            sa.String(100),
            nullable=True,
            comment="Estado del caso",
        ),
    )
    op.add_column(
        "ai_results",
        sa.Column(
            "final_category",
            sa.String(200),
            nullable=True,
            comment="Categoría final del caso",
        ),
    )


def downgrade() -> None:
    op.drop_column("ai_results", "final_category")
    op.drop_column("ai_results", "status")
    op.drop_column("ai_results", "case_type")
