"""Add column for table user

Revision ID: b9f4e8e003c6
Revises: a5c06e852f6e
Create Date: 2023-10-17 11:22:35.021195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9f4e8e003c6'
down_revision = 'a5c06e852f6e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('office', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('contact', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('contact')
        batch_op.drop_column('office')

    # ### end Alembic commands ###
