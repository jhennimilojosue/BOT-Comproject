"""003_create_catalogo_tiempos_table

Revision ID: 003
Revises: 002
Create Date: 2026-08-25
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "catalogo_tiempos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("nivel1", sa.String(200), nullable=False),
        sa.Column("nivel2", sa.String(200), nullable=False),
        sa.Column("nivel3", sa.String(200), nullable=True),
        sa.Column("path_completo", sa.String(500), nullable=False),
        sa.Column("path_normalizado", sa.String(500), nullable=False),
        sa.Column("tiempo_min", sa.Integer(), nullable=False),
        sa.Column("tiempo_max", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_catalogo_tiempos_path_normalizado",
        "catalogo_tiempos",
        ["path_normalizado"],
        unique=True,
    )
    op.create_index(
        "ix_catalogo_tiempos_nivel1",
        "catalogo_tiempos",
        ["nivel1"],
    )


def downgrade() -> None:
    op.drop_index("ix_catalogo_tiempos_nivel1")
    op.drop_index("ix_catalogo_tiempos_path_normalizado")
    op.drop_table("catalogo_tiempos")
