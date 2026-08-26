"""004_add_responsible_name_to_processings

Revision ID: 004
Revises: 003
Create Date: 2026-08-25
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "processings",
        sa.Column(
            "responsible_name",
            sa.String(200),
            nullable=True,
            comment="Nombre del responsable seleccionado para la ejecución",
        ),
    )
    op.create_index(
        "ix_processings_responsible_name",
        "processings",
        ["responsible_name"],
    )


def downgrade() -> None:
    op.drop_index("ix_processings_responsible_name")
    op.drop_column("processings", "responsible_name")
