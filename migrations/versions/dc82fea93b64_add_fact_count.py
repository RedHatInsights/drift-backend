"""add fact_count

Revision ID: dc82fea93b64
Revises: 1b7d3a5f6702
Create Date: 2019-06-19 13:57:50.865477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dc82fea93b64"
down_revision = "1b7d3a5f6702"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "system_baselines", sa.Column("fact_count", sa.Integer(), nullable=True)
    )


def downgrade():
    op.drop_column("system_baselines", "fact_count")
