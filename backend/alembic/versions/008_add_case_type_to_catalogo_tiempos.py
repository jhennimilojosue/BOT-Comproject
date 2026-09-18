"""008_add_case_type_to_catalogo_tiempos

Revision ID: 008
Revises: 007
Create Date: 2026-09-11
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columna case_type (Requerimiento como valor por defecto para registros existentes)
    op.add_column(
        "catalogo_tiempos",
        sa.Column(
            "case_type",
            sa.String(20),
            nullable=False,
            server_default="Requerimiento",
            comment="Tipo de caso (Incidente/Requerimiento)",
        ),
    )

    # Cambiar el índice único: ya no es único solo por path_normalizado,
    # ahora es único por (case_type, path_normalizado) para permitir que un
    # mismo path exista para Incidentes y Requerimientos con tiempos distintos.
    op.drop_index("ix_catalogo_tiempos_path_normalizado", table_name="catalogo_tiempos")
    op.create_index(
        "ix_catalogo_tiempos_case_type_path",
        "catalogo_tiempos",
        ["case_type", "path_normalizado"],
        unique=True,
    )
    op.create_index(
        "ix_catalogo_tiempos_path_normalizado",
        "catalogo_tiempos",
        ["path_normalizado"],
    )


def downgrade() -> None:
    op.drop_index("ix_catalogo_tiempos_case_type_path", table_name="catalogo_tiempos")
    op.drop_index("ix_catalogo_tiempos_path_normalizado", table_name="catalogo_tiempos")
    op.create_index(
        "ix_catalogo_tiempos_path_normalizado",
        "catalogo_tiempos",
        ["path_normalizado"],
        unique=True,
    )
    op.drop_column("catalogo_tiempos", "case_type")