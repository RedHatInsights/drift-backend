"""empty message

Revision ID: 5d70f1a702c2
Revises: ec54379095ca
Create Date: 2022-06-15 17:58:31.670001

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "5d70f1a702c2"
down_revision = "ec54379095ca"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "system_baselines",
        sa.Column("org_id", sa.String(length=36), nullable=True),
    )
    op.create_index(
        op.f("ix_system_baselines_org_id"),
        "system_baselines",
        ["org_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_system_baselines_org_id"),
        table_name="system_baselines",
    )
    op.drop_column("system_baselines", "org_id")
