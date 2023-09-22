"""with barangay

Revision ID: 14061d6ab540
Revises: cdab736817c8
Create Date: 2023-09-19 13:20:10.462060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14061d6ab540'
down_revision = 'cdab736817c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('barangay', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.drop_column('barangay')

    # ### end Alembic commands ###
