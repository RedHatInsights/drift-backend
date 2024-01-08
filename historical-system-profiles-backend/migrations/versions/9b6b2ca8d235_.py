"""add inventory_id index

Revision ID: 9b6b2ca8d235
Revises: 6c97901967f3
Create Date: 2020-06-19 08:24:01.039562

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "9b6b2ca8d235"
down_revision = "6c97901967f3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        op.f("ix_historical_system_profiles_inventory_id"),
        "historical_system_profiles",
        ["inventory_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_historical_system_profiles_inventory_id"),
        table_name="historical_system_profiles",
    )
