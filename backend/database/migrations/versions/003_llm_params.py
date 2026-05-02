"""add llm_params and channel_id

Revision ID: 003
Revises: 002
Create Date: 2026-05-02
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('llm_params', sa.Text(), nullable=True))
    op.add_column('chats', sa.Column(
        'channel_id', sa.String(20), nullable=True))
    op.add_column('chats', sa.Column('active', sa.Boolean(),
                  server_default='true', nullable=False))


def downgrade():
    op.drop_column('users', 'llm_params')
    op.drop_column('chats', 'channel_id')
    op.drop_column('chats', 'active')
