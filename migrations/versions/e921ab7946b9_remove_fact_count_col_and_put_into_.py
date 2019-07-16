"""remove fact_count col and put into property

Revision ID: e921ab7946b9
Revises: dc82fea93b64
Create Date: 2019-07-16 14:58:00.387840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e921ab7946b9"
down_revision = "dc82fea93b64"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("system_baselines", "fact_count")


def downgrade():
    op.add_column(
        "system_baselines",
        sa.Column("fact_count", sa.INTEGER(), autoincrement=False, nullable=True),
    )
