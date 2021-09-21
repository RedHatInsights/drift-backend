"""add notification enabled flag to baselines

Revision ID: ec54379095ca
Revises: 63a89136a199
Create Date: 2021-09-21 17:23:18.406934

"""
import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = "ec54379095ca"
down_revision = "8b43e87e0e47"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "system_baselines", sa.Column("notifications_enabled", sa.Boolean(), nullable=False)
    )


def downgrade():
    op.drop_column("system_baselines", "notifications_enabled")
