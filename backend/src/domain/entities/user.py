from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.entities.project import Project


@dataclass
class User:
    """用户领域实体"""
    id: str
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def can_manage_project(self, project: "Project") -> bool:
        """检查用户是否有权限管理项目"""
        return self.is_superuser or project.owner_id == self.id
