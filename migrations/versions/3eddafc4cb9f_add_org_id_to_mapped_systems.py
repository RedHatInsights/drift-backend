"""empty message

Revision ID: 3eddafc4cb9f
Revises: 5d70f1a702c2
Create Date: 2022-06-15 18:15:36.830059

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "3eddafc4cb9f"
down_revision = "5d70f1a702c2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "system_baseline_mapped_systems",
        sa.Column("org_id", sa.String(length=36), nullable=True),
    )
    op.create_index(
        op.f("ix_system_baseline_mapped_systems_org_id"),
        "system_baseline_mapped_systems",
        ["org_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_system_baseline_mapped_systems_org_id"),
        table_name="system_baseline_mapped_systems",
    )
    op.drop_column("system_baseline_mapped_systems", "org_id")
