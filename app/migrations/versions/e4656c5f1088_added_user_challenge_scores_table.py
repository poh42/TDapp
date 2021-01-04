"""Added user_challenge_scores table

Revision ID: e4656c5f1088
Revises: 707baa1bc549
Create Date: 2020-12-28 16:13:42.959417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4656c5f1088"
down_revision = "3b4f2a2aae35"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_challenge_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("own_score", sa.Integer(), nullable=False),
        sa.Column("opponent_score", sa.Integer(), nullable=False),
        sa.Column("screenshot", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["challenge_id"],
            ["challenges.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_challenge_scores")
    # ### end Alembic commands ###
