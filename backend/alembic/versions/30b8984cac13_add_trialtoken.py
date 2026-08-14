"""Add TrialToken

Revision ID: 30b8984cac13
Revises: 6add7104c7c0
Create Date: 2026-08-14 22:17:21.600538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30b8984cac13'
down_revision: Union[str, Sequence[str], None] = '6add7104c7c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('trial_tokens',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('token_string', sa.String(), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(), nullable=True),
    sa.Column('updated_by', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trial_tokens_id'), 'trial_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_trial_tokens_token_string'), 'trial_tokens', ['token_string'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_trial_tokens_token_string'), table_name='trial_tokens')
    op.drop_index(op.f('ix_trial_tokens_id'), table_name='trial_tokens')
    op.drop_table('trial_tokens')
