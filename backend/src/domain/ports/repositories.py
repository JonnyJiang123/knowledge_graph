from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from src.domain.entities.data_source import DataSource
from src.domain.entities.ingestion_job import IngestionJob
from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.domain.value_objects.ingestion import FileArtifact, JobStatus


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User: ...

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: ...


class ProjectRepository(ABC):
    @abstractmethod
    async def create(self, project: Project) -> Project: ...

    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[Project]: ...

    @abstractmethod
    async def list_by_owner(self, owner_id: str) -> list[Project]: ...

    @abstractmethod
    async def update(self, project: Project) -> Project: ...

    @abstractmethod
    async def delete(self, project_id: str) -> None: ...


class DataSourceRepository(ABC):
    @abstractmethod
    async def create(self, source: DataSource) -> DataSource: ...

    @abstractmethod
    async def update(self, source: DataSource) -> DataSource: ...

    @abstractmethod
    async def list(self, project_id: str) -> list[DataSource]: ...

    @abstractmethod
    async def get(self, source_id: str) -> Optional[DataSource]: ...


class IngestionJobRepository(ABC):
    @abstractmethod
    async def create(self, job: IngestionJob) -> IngestionJob: ...

    @abstractmethod
    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        processed_rows: Optional[int] = None,
        result_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None: ...

    @abstractmethod
    async def get(self, job_id: str) -> Optional[IngestionJob]: ...

    @abstractmethod
    async def list(self, project_id: str) -> list[IngestionJob]: ...


class FileStoragePort(ABC):
    @abstractmethod
    async def save(self, artifact: FileArtifact, data: bytes) -> FileArtifact: ...

    @abstractmethod
    async def delete(self, stored_path: str) -> None: ...


class PreviewCachePort(ABC):
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]: ...


class TaskQueuePort(ABC):
    @abstractmethod
    async def enqueue(self, task_name: str, payload: dict[str, Any]) -> str: ...
