"""Adding winner_id column to results1v1

Revision ID: dd8fcd114129
Revises: e42053be882c
Create Date: 2020-11-23 16:38:38.869674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dd8fcd114129"
down_revision = "e42053be882c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("results_1v1", sa.Column("winner_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "results_1v1", "users", ["winner_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "results_1v1", type_="foreignkey")
    op.drop_column("results_1v1", "winner_id")
    # ### end Alembic commands ###
