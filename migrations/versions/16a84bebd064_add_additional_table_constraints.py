"""add additional table constraints

Revision ID: 16a84bebd064
Revises: e921ab7946b9
Create Date: 2019-07-29 13:45:44.389108

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "16a84bebd064"
down_revision = "e921ab7946b9"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "system_baselines",
        "account",
        existing_type=sa.VARCHAR(length=10),
        nullable=False,
    )
    op.alter_column(
        "system_baselines",
        "created_on",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.alter_column(
        "system_baselines",
        "display_name",
        existing_type=sa.VARCHAR(length=200),
        nullable=False,
    )
    op.alter_column(
        "system_baselines",
        "modified_on",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.create_unique_constraint(
        "_account_display_name_uc", "system_baselines", ["account", "display_name"]
    )


def downgrade():
    op.drop_constraint("_account_display_name_uc", "system_baselines", type_="unique")
    op.alter_column(
        "system_baselines",
        "modified_on",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.alter_column(
        "system_baselines",
        "display_name",
        existing_type=sa.VARCHAR(length=200),
        nullable=True,
    )
    op.alter_column(
        "system_baselines",
        "created_on",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.alter_column(
        "system_baselines",
        "account",
        existing_type=sa.VARCHAR(length=10),
        nullable=True,
    )
