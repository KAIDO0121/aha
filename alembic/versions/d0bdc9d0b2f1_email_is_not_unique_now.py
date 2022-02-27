"""Email is not unique now

Revision ID: d0bdc9d0b2f1
Revises: 608e6ef2ec8e
Create Date: 2022-02-27 21:58:12.683333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0bdc9d0b2f1'
down_revision = '608e6ef2ec8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_email', table_name='users')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index('ix_users_email', 'users', ['email'], unique=False)
    # ### end Alembic commands ###