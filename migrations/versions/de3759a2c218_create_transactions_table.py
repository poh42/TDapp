"""Create transactions table

Revision ID: de3759a2c218
Revises: 3c18c08b9f0c
Create Date: 2020-10-29 11:24:22.862779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "de3759a2c218"
down_revision = "3c18c08b9f0c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "previous_credit_total", sa.Numeric(precision=10, scale=2), nullable=False
        ),
        sa.Column("credit_change", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("credit_total", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=60), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["challenge_id"], ["challenges.id"],),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("transactions")
    # ### end Alembic commands ###
