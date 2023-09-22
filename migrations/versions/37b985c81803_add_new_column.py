"""Add new column

Revision ID: 37b985c81803
Revises: 292978e88d59
Create Date: 2023-08-30 12:05:07.143122

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37b985c81803'
down_revision = '292978e88d59'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('type')

    # ### end Alembic commands ###