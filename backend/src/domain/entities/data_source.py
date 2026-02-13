from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Callable, Optional

from src.domain.value_objects.ingestion import DataSourceType, FileFormat

MaskFn = Callable[[str], str]


def _default_mask(value: str) -> str:
    return value


@dataclass
class DataSource:
    id: str
    project_id: str
    name: str
    type: DataSourceType
    config: dict[str, Any]
    status: str = "ACTIVE"
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def create_mysql(
        cls,
        project_id: str,
        name: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        encrypt: MaskFn | None = None,
    ) -> "DataSource":
        encrypt = encrypt or _default_mask
        config = {
            "host": host,
            "port": port,
            "database": database,
            "username": username,
            "password": encrypt(password),
        }
        return cls(
            id="",
            project_id=project_id,
            name=name,
            type=DataSourceType.MYSQL,
            config=config,
        )

    @classmethod
    def create_file(
        cls,
        project_id: str,
        name: str,
        file_format: FileFormat,
        original_filename: str,
        stored_path: str,
        size_bytes: int,
        uploaded_by: str,
        uploaded_at: datetime,
    ) -> "DataSource":
        config = {
            "file_format": file_format,
            "original_filename": original_filename,
            "stored_path": stored_path,
            "size_bytes": size_bytes,
            "uploaded_by": uploaded_by,
            "uploaded_at": uploaded_at.isoformat(),
        }
        return cls(
            id="",
            project_id=project_id,
            name=name,
            type=DataSourceType.FILE,
            config=config,
        )

    def mark_used(self) -> None:
        self.last_used_at = datetime.now(UTC)

    def safe_summary(self) -> dict[str, Any]:
        summary = {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "config": dict(self.config),
        }
        password = summary["config"].get("password")
        if password is not None:
            summary["config"]["password"] = "********"
        return summary
