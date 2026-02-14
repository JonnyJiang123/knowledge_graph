"""add graph projects table

Revision ID: 20260213_graph_projects
Revises: 20260212_ingestion
Create Date: 2026-02-13
"""

from alembic import op
import sqlalchemy as sa


revision = "20260213_graph_projects"
down_revision = "20260212_ingestion"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "graph_projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_graph_projects_owner_id", "graph_projects", ["owner_id"])
    op.create_index("ix_graph_projects_name", "graph_projects", ["name"])


def downgrade() -> None:
    op.drop_index("ix_graph_projects_name", table_name="graph_projects")
    op.drop_index("ix_graph_projects_owner_id", table_name="graph_projects")
    op.drop_table("graph_projects")
