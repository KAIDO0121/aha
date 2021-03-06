"""add login times column

Revision ID: 608e6ef2ec8e
Revises: 02ff98d9e04a
Create Date: 2022-02-20 23:20:12.479454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '608e6ef2ec8e'
down_revision = '02ff98d9e04a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('login_times', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'login_times')
    # ### end Alembic commands ###
