"""Adding game_has_console table

Revision ID: 64eabdd635e6
Revises: a5148d170733
Create Date: 2020-10-23 16:08:48.334168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "64eabdd635e6"
down_revision = "a5148d170733"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "games_has_consoles",
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("console_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["console_id"], ["consoles.id"],),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"],),
        sa.PrimaryKeyConstraint("game_id", "console_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("games_has_consoles")
    # ### end Alembic commands ###
