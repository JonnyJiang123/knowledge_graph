"""create core user and project tables

Revision ID: 20260211_core_tables
Revises: None
Create Date: 2026-02-13
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.exc import OperationalError


revision = "20260211_core_tables"
down_revision = None
branch_labels = None
depends_on = None


MYSQL_TABLE_EXISTS = 1050
MYSQL_INDEX_EXISTS = 1061


def _safe_create_table(name: str, *columns: sa.Column, **kwargs) -> None:
    try:
        op.create_table(name, *columns, **kwargs)
    except OperationalError as exc:  # pragma: no cover - depends on DB state
        code = getattr(getattr(exc, "orig", None), "args", [None])[0]
        if code != MYSQL_TABLE_EXISTS:
            raise


def _safe_create_index(name: str, table_name: str, columns, **kwargs) -> None:
    try:
        op.create_index(name, table_name, columns, **kwargs)
    except OperationalError as exc:  # pragma: no cover
        code = getattr(getattr(exc, "orig", None), "args", [None])[0]
        if code != MYSQL_INDEX_EXISTS:
            raise


def upgrade() -> None:
    _safe_create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False, unique=True),
        sa.Column("email", sa.String(length=100), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    _safe_create_index("ix_users_username", "users", ["username"], unique=True)
    _safe_create_index("ix_users_email", "users", ["email"], unique=True)

    _safe_create_table(
        "projects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(length=20), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    _safe_create_index("ix_projects_name", "projects", ["name"])
    _safe_create_index("ix_projects_owner_id", "projects", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_index("ix_projects_name", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
