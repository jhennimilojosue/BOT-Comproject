"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-08-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create uploads table
    op.create_table(
        'uploads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('total_cases', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        comment='Tabla de cargas de archivos'
    )

    # Create cases table
    op.create_table(
        'cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('upload_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('uploads.id'), nullable=False),
        sa.Column('case_code', sa.String(50), nullable=False),
        sa.Column('case_type', sa.String(20), nullable=False),
        sa.Column('responsible_name', sa.String(200), nullable=False),
        sa.Column('responsible_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_name', sa.String(200), nullable=True),
        sa.Column('project', sa.String(200), nullable=False),
        sa.Column('registered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(100), nullable=False),
        sa.Column('final_category', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('solution', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        comment='Tabla de casos de Aranda'
    )

    # Create indexes for cases
    op.create_index('ix_cases_upload_id', 'cases', ['upload_id'])
    op.create_index('ix_cases_case_code', 'cases', ['case_code'])
    op.create_index('ix_cases_upload_case_code', 'cases', ['upload_id', 'case_code'], unique=True)

    # Create processings table
    op.create_table(
        'processings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('upload_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('uploads.id'), nullable=False),
        sa.Column('responsible_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('total_cases', sa.Integer, nullable=True),
        sa.Column('processed_cases', sa.Integer, nullable=True),
        sa.Column('rejected_cases', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        comment='Tabla de ejecuciones de procesamiento'
    )

    # Create indexes for processings
    op.create_index('ix_processings_upload_id', 'processings', ['upload_id'])
    op.create_index('ix_processings_responsible_id', 'processings', ['responsible_id'])

    # Create processing_rejections table
    op.create_table(
        'processing_rejections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('processing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('processings.id'), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('case_code', sa.String(50), nullable=False),
        sa.Column('reason_code', sa.String(50), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        comment='Tabla de rechazos de procesamiento'
    )

    # Create indexes for processing_rejections
    op.create_index('ix_processing_rejections_processing_id', 'processing_rejections', ['processing_id'])
    op.create_index('ix_processing_rejections_case_id', 'processing_rejections', ['case_id'])

    # Create estimations table
    op.create_table(
        'estimations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('processing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('processings.id'), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('case_code', sa.String(50), nullable=False),
        sa.Column('estimated_minutes', sa.Integer, nullable=False),
        sa.Column('minimum_minutes', sa.Integer, nullable=False),
        sa.Column('maximum_minutes', sa.Integer, nullable=False),
        sa.Column('final_category', sa.String(200), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='VALID'),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        comment='Tabla de estimaciones de tiempo'
    )

    # Create indexes for estimations
    op.create_index('ix_estimations_processing_id', 'estimations', ['processing_id'])
    op.create_index('ix_estimations_case_id', 'estimations', ['case_id'])

    # Create ai_results table
    op.create_table(
        'ai_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('processing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('processings.id'), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('case_code', sa.String(50), nullable=False),
        sa.Column('estimated_minutes', sa.Integer, nullable=False),
        sa.Column('generated_description', sa.Text, nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('tokens_used', sa.Integer, nullable=True),
        sa.Column('latency_ms', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        comment='Tabla de resultados de IA'
    )

    # Create indexes for ai_results
    op.create_index('ix_ai_results_processing_id', 'ai_results', ['processing_id'])
    op.create_index('ix_ai_results_case_id', 'ai_results', ['case_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('ai_results')
    op.drop_table('estimations')
    op.drop_table('processing_rejections')
    op.drop_table('processings')
    op.drop_table('cases')
    op.drop_table('uploads')
