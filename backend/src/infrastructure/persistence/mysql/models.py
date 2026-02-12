from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.mysql.database import Base


def generate_uuid() -> str:
    return str(uuid4())


class UserModel(Base):
    """用户模型"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    projects: Mapped[list["ProjectModel"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class ProjectModel(Base):
    """项目模型"""
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    industry: Mapped[str] = mapped_column(String(20))  # FINANCE, HEALTHCARE
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["UserModel"] = relationship(back_populates="projects")
    data_sources: Mapped[list["DataSourceModel"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list["UploadArtifactModel"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class DataSourceModel(Base):
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20))
    config: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["ProjectModel"] = relationship(back_populates="data_sources")
    artifacts: Mapped[list["UploadArtifactModel"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["IngestionJobModel"]] = relationship(back_populates="source")


class UploadArtifactModel(Base):
    __tablename__ = "upload_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    source_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("data_sources.id"), nullable=True
    )
    file_format: Mapped[str] = mapped_column(String(10))
    stored_path: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[str] = mapped_column(String(255))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    project: Mapped["ProjectModel"] = relationship(back_populates="artifacts")
    source: Mapped[Optional["DataSourceModel"]] = relationship(back_populates="artifacts")
    jobs: Mapped[list["IngestionJobModel"]] = relationship(
        back_populates="artifact", cascade="all, delete-orphan"
    )


class CleaningRuleModel(Base):
    __tablename__ = "cleaning_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(100))
    target_field: Mapped[str] = mapped_column(String(100))
    rule_type: Mapped[str] = mapped_column(String(20))
    params: Mapped[dict] = mapped_column(JSON)
    severity: Mapped[str] = mapped_column(String(20), default="ERROR")
    created_by: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class IngestionJobModel(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    artifact_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("upload_artifacts.id"), nullable=False
    )
    source_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("data_sources.id"), nullable=True
    )
    mode: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20), index=True)
    total_rows: Mapped[int] = mapped_column(Integer)
    processed_rows: Mapped[int] = mapped_column(Integer, default=0)
    result_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    project: Mapped["ProjectModel"] = relationship()
    artifact: Mapped["UploadArtifactModel"] = relationship(back_populates="jobs")
    source: Mapped[Optional["DataSourceModel"]] = relationship(back_populates="jobs")
