"""Removing name from challenges

Revision ID: e42053be882c
Revises: 1c8040ae118a
Create Date: 2020-11-23 12:16:42.758182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e42053be882c'
down_revision = '1c8040ae118a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('challenges', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('challenges', sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
