"""init

Revision ID: 0001_init
Revises: None
Create Date: 2026-02-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("tier_code", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_accounts_email", "accounts", ["email"], unique=True)

    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("base", sa.String(length=200), nullable=False),
        sa.Column("command_team", sa.String(length=500), nullable=False),
        sa.Column("tier_code", sa.String(length=32), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"], unique=True)

    op.create_table(
        "service_members",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("creator_account_id", sa.String(length=36), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("subject_account_id", sa.String(length=36), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("branch", sa.String(length=64), nullable=False),
        sa.Column("component", sa.String(length=64), nullable=False),
        sa.Column("stp_data", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("claim_code", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_service_members_creator", "service_members", ["creator_account_id"])
    op.create_index("ix_service_members_subject", "service_members", ["subject_account_id"])
    op.create_index("ix_service_members_branch", "service_members", ["branch"])
    op.create_index("ix_service_members_component", "service_members", ["component"])
    op.create_index("ix_service_members_claim_code", "service_members", ["claim_code"])

    op.create_table(
        "service_member_shares",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("service_member_id", sa.String(length=36), sa.ForeignKey("service_members.id"), nullable=False),
        sa.Column("target_account_id", sa.String(length=36), sa.ForeignKey("accounts.id"), nullable=True),
        sa.Column("target_org_id", sa.String(length=36), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("permission", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
    )
    op.create_index("ix_shares_sm", "service_member_shares", ["service_member_id"])
    op.create_index("ix_shares_target_account", "service_member_shares", ["target_account_id"])
    op.create_index("ix_shares_target_org", "service_member_shares", ["target_org_id"])

    op.create_table(
        "upload_files",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("service_member_id", sa.String(length=36), sa.ForeignKey("service_members.id"), nullable=False),
        sa.Column("spot_key", sa.String(length=64), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_upload_sm", "upload_files", ["service_member_id"])
    op.create_index("ix_upload_spot", "upload_files", ["spot_key"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("actor_type", sa.String(length=16), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=120), nullable=False),
        sa.Column("target_type", sa.String(length=32), nullable=False),
        sa.Column("target_id", sa.String(length=36), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

def downgrade():
    op.drop_table("audit_logs")
    op.drop_index("ix_upload_spot", table_name="upload_files")
    op.drop_index("ix_upload_sm", table_name="upload_files")
    op.drop_table("upload_files")
    op.drop_index("ix_shares_target_org", table_name="service_member_shares")
    op.drop_index("ix_shares_target_account", table_name="service_member_shares")
    op.drop_index("ix_shares_sm", table_name="service_member_shares")
    op.drop_table("service_member_shares")
    op.drop_index("ix_service_members_claim_code", table_name="service_members")
    op.drop_index("ix_service_members_component", table_name="service_members")
    op.drop_index("ix_service_members_branch", table_name="service_members")
    op.drop_index("ix_service_members_subject", table_name="service_members")
    op.drop_index("ix_service_members_creator", table_name="service_members")
    op.drop_table("service_members")
    op.drop_index("ix_organizations_name", table_name="organizations")
    op.drop_table("organizations")
    op.drop_index("ix_accounts_email", table_name="accounts")
    op.drop_table("accounts")