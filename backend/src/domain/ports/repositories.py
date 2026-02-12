from abc import ABC, abstractmethod
from typing import Any, Optional

from src.domain.entities.user import User
from src.domain.entities.project import Project
from src.domain.entities.data_source import DataSource
from src.domain.entities.ingestion_job import IngestionJob
from src.domain.value_objects.ingestion import FileArtifact, JobStatus


class UserRepository(ABC):
    """用户仓储接口"""

    @abstractmethod
    async def create(self, user: User) -> User:
        """创建用户"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        pass


class ProjectRepository(ABC):
    """项目仓储接口"""

    @abstractmethod
    async def create(self, project: Project) -> Project:
        """创建项目"""
        pass


class DataSourceRepository(ABC):
    """Data source persistence port."""

    @abstractmethod
    async def create(self, source: DataSource) -> DataSource:
        pass

    @abstractmethod
    async def update(self, source: DataSource) -> DataSource:
        pass

    @abstractmethod
    async def list(self, project_id: str) -> list[DataSource]:
        pass

    @abstractmethod
    async def get(self, source_id: str) -> Optional[DataSource]:
        pass


class IngestionJobRepository(ABC):
    """Ingestion job persistence port."""

    @abstractmethod
    async def create(self, job: IngestionJob) -> IngestionJob:
        pass

    @abstractmethod
    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        processed_rows: Optional[int] = None,
        result_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    async def get(self, job_id: str) -> Optional[IngestionJob]:
        pass

    @abstractmethod
    async def list(self, project_id: str) -> list[IngestionJob]:
        pass


class FileStoragePort(ABC):
    """Abstract storage backend for uploaded artifacts."""

    @abstractmethod
    async def save(self, artifact: FileArtifact, data: bytes) -> FileArtifact:
        pass

    @abstractmethod
    async def delete(self, stored_path: str) -> None:
        pass


class PreviewCachePort(ABC):
    """Cache service for ingestion previews."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass


class TaskQueuePort(ABC):
    """Background task queue abstraction."""

    @abstractmethod
    async def enqueue(self, task_name: str, payload: dict[str, Any]) -> str:
        pass

    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """根据ID获取项目"""
        pass

    @abstractmethod
    async def list_by_owner(self, owner_id: str) -> list[Project]:
        """获取用户的所有项目"""
        pass

    @abstractmethod
    async def update(self, project: Project) -> Project:
        """更新项目"""
        pass

    @abstractmethod
    async def delete(self, project_id: str) -> None:
        """删除项目"""
        pass
