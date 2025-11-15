"""Add index on log_entries.timestamp for timeline queries

Revision ID: 002_add_index_ts
Revises: 398c3aed8118
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_index_ts'
down_revision = '398c3aed8118'
branch_labels = None
depends_on = None


def upgrade():
    # Create index on timestamp column for efficient timeline queries
    # Note: Using the exact index name requested by user (with typo preserved)
    op.create_index(
        'idx_log_entires_ts',
        'log_entries',
        ['timestamp'],
        if_not_exists=True
    )


def downgrade():
    op.drop_index('idx_log_entires_ts', table_name='log_entries')

