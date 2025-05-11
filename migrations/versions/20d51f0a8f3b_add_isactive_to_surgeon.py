"""Add IsActive to Surgeon

Revision ID: 20d51f0a8f3b
Revises: 
Create Date: 2023-11-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20d51f0a8f3b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # This is a retroactive migration file to document what we already did manually
    # via direct SQL ALTER TABLE statement
    op.add_column('Surgeon', sa.Column('IsActive', sa.Boolean(), nullable=True, server_default='1'))


def downgrade():
    op.drop_column('Surgeon', 'IsActive') 