"""Adding is admin column

Revision ID: 9a5b3ed8dd5b
Revises: f2c67b529235
Create Date: 2020-10-14 15:15:16.912711

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a5b3ed8dd5b'
down_revision = 'f2c67b529235'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True, default=False))


def downgrade():
    op.drop_column('users', 'is_admin')
