"""Initial migration

Revision ID: 292978e88d59
Revises: 1b9e1467220f
Create Date: 2023-08-19 16:37:37.326074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '292978e88d59'
down_revision = '1b9e1467220f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.alter_column('date_created',
               existing_type=sa.DATE(),
               type_=sa.DateTime(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.alter_column('date_created',
               existing_type=sa.DateTime(),
               type_=sa.DATE(),
               existing_nullable=True)

    # ### end Alembic commands ###
