"""add support verify codes

Revision ID: 292ee3aac2b7
Revises: 0001_init
Create Date: 2026-02-27 02:35:31.220011
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "292ee3aac2b7"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "support_verify_codes",

        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),

        sa.Column(
            "actor_account_id",
            sa.String(length=36),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
        ),

        sa.Column(
            "code",
            sa.String(length=6),
            nullable=False,
        ),

        sa.Column(
            "is_used",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),

        sa.CheckConstraint(
            "char_length(code) = 6",
            name="ck_support_verify_code_length",
        ),
    )

    op.create_index(
        "ix_support_verify_actor",
        "support_verify_codes",
        ["actor_account_id"],
    )

    op.create_index(
        "ix_support_verify_code",
        "support_verify_codes",
        ["code"],
    )


def downgrade():

    op.drop_index("ix_support_verify_code", table_name="support_verify_codes")
    op.drop_index("ix_support_verify_actor", table_name="support_verify_codes")
    op.drop_table("support_verify_codes")