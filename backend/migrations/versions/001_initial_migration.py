"""Initial migration: create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create log_files table
    op.create_table('log_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('status', sa.String(50), nullable=False, server_default='uploading'),
        sa.Column('total_entries', sa.Integer(), server_default='0'),
        sa.Column('date_range_start', sa.DateTime(), nullable=True),
        sa.Column('date_range_end', sa.DateTime(), nullable=True),
        sa.Column('file_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
    )
    
    # Create log_entries table
    op.create_table('log_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('log_file_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('protocol', sa.String(10), nullable=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('action', sa.String(50), nullable=True),
        sa.Column('app_name', sa.String(100), nullable=True),
        sa.Column('app_class', sa.String(100), nullable=True),
        sa.Column('throttle_req_size', sa.Integer(), nullable=True),
        sa.Column('throttle_resp_size', sa.Integer(), nullable=True),
        sa.Column('req_size', sa.Integer(), nullable=True),
        sa.Column('resp_size', sa.Integer(), nullable=True),
        sa.Column('url_class', sa.String(100), nullable=True),
        sa.Column('url_supercat', sa.String(100), nullable=True),
        sa.Column('url_cat', sa.String(100), nullable=True),
        sa.Column('dlp_dict', sa.String(100), nullable=True),
        sa.Column('dlp_eng', sa.String(100), nullable=True),
        sa.Column('dlp_hits', sa.Integer(), server_default='0'),
        sa.Column('file_class', sa.String(100), nullable=True),
        sa.Column('file_type', sa.String(100), nullable=True),
        sa.Column('location2', sa.String(100), nullable=True),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('client_ip', postgresql.INET(), nullable=True),
        sa.Column('server_ip', postgresql.INET(), nullable=True),
        sa.Column('http_method', sa.String(10), nullable=True),
        sa.Column('http_status', sa.Integer(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('threat_category', sa.String(100), nullable=True),
        sa.Column('fw_filter', sa.String(100), nullable=True),
        sa.Column('fw_rule', sa.String(100), nullable=True),
        sa.Column('policy_type', sa.String(100), nullable=True),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.Column('is_anomalous', sa.Boolean(), server_default='false'),
        sa.Column('anomaly_type', sa.String(50), nullable=True),
        sa.Column('anomaly_reason', sa.Text(), nullable=True),
        sa.Column('anomaly_confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['log_file_id'], ['log_files.id'], ),
    )
    op.create_index(op.f('ix_log_entries_log_file_id'), 'log_entries', ['log_file_id'], unique=False)
    op.create_index(op.f('ix_log_entries_timestamp'), 'log_entries', ['timestamp'], unique=False)
    op.create_index(op.f('ix_log_entries_domain'), 'log_entries', ['domain'], unique=False)
    op.create_index(op.f('ix_log_entries_action'), 'log_entries', ['action'], unique=False)
    op.create_index(op.f('ix_log_entries_url_cat'), 'log_entries', ['url_cat'], unique=False)
    op.create_index(op.f('ix_log_entries_department'), 'log_entries', ['department'], unique=False)
    op.create_index(op.f('ix_log_entries_client_ip'), 'log_entries', ['client_ip'], unique=False)
    op.create_index(op.f('ix_log_entries_threat_category'), 'log_entries', ['threat_category'], unique=False)
    op.create_index(op.f('ix_log_entries_is_anomalous'), 'log_entries', ['is_anomalous'], unique=False)
    op.create_index('idx_log_entries_log_file_timestamp', 'log_entries', ['log_file_id', 'timestamp'], unique=False)
    
    # Create user_risk_scores table
    op.create_table('user_risk_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('log_file_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_identifier', sa.String(255), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('anomaly_count', sa.Integer(), server_default='0'),
        sa.Column('blocked_count', sa.Integer(), server_default='0'),
        sa.Column('malicious_domain_count', sa.Integer(), server_default='0'),
        sa.Column('calculated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('score_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['log_file_id'], ['log_files.id'], ),
    )
    op.create_index('idx_user_risk_scores_user', 'user_risk_scores', ['user_identifier'], unique=False)
    op.create_index('idx_user_risk_scores_log_file', 'user_risk_scores', ['log_file_id'], unique=False)


def downgrade():
    op.drop_table('user_risk_scores')
    op.drop_table('log_entries')
    op.drop_table('log_files')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

