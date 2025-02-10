"""Recreate migration

Revision ID: 7139df155d47
Revises: e064b5ecc124
Create Date: 2023-11-17 09:48:43.764926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7139df155d47'
down_revision = 'e064b5ecc124'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cases', sa.Column('category', sa.String(length=10), nullable=True))


def downgrade():
    pass
