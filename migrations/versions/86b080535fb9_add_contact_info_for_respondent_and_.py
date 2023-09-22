"""Add contact info for respondent and complainant

Revision ID: 86b080535fb9
Revises: 37b985c81803
Create Date: 2023-09-07 08:57:09.936176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86b080535fb9'
down_revision = '37b985c81803'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contact_complainant', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('contact_respondent', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cases', schema=None) as batch_op:
        batch_op.drop_column('contact_respondent')
        batch_op.drop_column('contact_complainant')

    # ### end Alembic commands ###
