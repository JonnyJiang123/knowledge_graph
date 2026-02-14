"""add ingestion tables

Revision ID: 20260212_ingestion
Revises: None
Create Date: 2026-02-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260212_ingestion"
down_revision = "20260211_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_data_sources_project_id",
        "data_sources",
        ["project_id"],
    )

    op.create_table(
        "upload_artifacts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=True),
        sa.Column("file_format", sa.String(length=10), nullable=False),
        sa.Column("stored_path", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
    )
    op.create_index(
        "ix_upload_artifacts_project_id",
        "upload_artifacts",
        ["project_id"],
    )

    op.create_table(
        "cleaning_rules",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("target_field", sa.String(length=100), nullable=False),
        sa.Column("rule_type", sa.String(length=20), nullable=False),
        sa.Column("params", sa.JSON(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="ERROR"),
        sa.Column("created_by", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("artifact_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=True),
        sa.Column("mode", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("processed_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("result_path", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_ingestion_jobs_project_id",
        "ingestion_jobs",
        ["project_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_ingestion_jobs_project_id", table_name="ingestion_jobs")
    op.drop_table("ingestion_jobs")
    op.drop_table("cleaning_rules")
    op.drop_index("ix_upload_artifacts_project_id", table_name="upload_artifacts")
    op.drop_table("upload_artifacts")
    op.drop_index("ix_data_sources_project_id", table_name="data_sources")
    op.drop_table("data_sources")
