"""010_unique_ai_results

Revision ID: 010
Revises: 009
Create Date: 2026-10-09
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DELETE FROM ai_results a
        USING ai_results b
        WHERE a.id > b.id
          AND a.processing_id = b.processing_id
          AND a.case_id = b.case_id
    """)
    op.create_unique_constraint(
        "uq_ai_results_processing_case",
        "ai_results",
        ["processing_id", "case_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_ai_results_processing_case", "ai_results")