"""empty message

Revision ID: e07ac5a2cd11
Revises: 46636756274e
Create Date: 2022-06-15 15:54:08.162382

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "e07ac5a2cd11"
down_revision = "46636756274e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "historical_system_profiles",
        sa.Column("org_id", sa.String(length=36), nullable=True),
    )
    op.create_index(
        op.f("ix_historical_system_profiles_org_id"),
        "historical_system_profiles",
        ["org_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_historical_system_profiles_org_id"),
        table_name="historical_system_profiles",
    )
    op.drop_column("historical_system_profiles", "org_id")
