from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.user import User
from src.domain.entities.project import Project


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
