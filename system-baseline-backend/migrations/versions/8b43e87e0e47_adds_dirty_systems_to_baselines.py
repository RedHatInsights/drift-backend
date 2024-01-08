"""Adds dirty_systems to baselines

Revision ID: 8b43e87e0e47
Revises: 63a89136a199
Create Date: 2021-10-06 17:52:31.050100

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "8b43e87e0e47"
down_revision = "63a89136a199"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("system_baselines", sa.Column("dirty_systems", sa.Boolean(), nullable=True))

    system_baselines_table = sa.sql.table(
        "system_baselines", sa.sql.column("dirty_systems", sa.Boolean)
    )
    op.execute(system_baselines_table.update().values({"dirty_systems": op.inline_literal(True)}))


def downgrade():
    op.drop_column("system_baselines", "dirty_systems")
