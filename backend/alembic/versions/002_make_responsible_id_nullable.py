"""Make responsible_id nullable in processings

Revision ID: 002
Revises: 001
Create Date: 2026-08-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make responsible_id nullable in processings table
    op.alter_column('processings', 'responsible_id',
                     existing_type=postgresql.UUID(as_uuid=True),
                     nullable=True)


def downgrade() -> None:
    # Make responsible_id NOT NULL again
    op.alter_column('processings', 'responsible_id',
                     existing_type=postgresql.UUID(as_uuid=True),
                     nullable=False)
