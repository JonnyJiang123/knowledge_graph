from typing import Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.project import Project
from src.domain.ports.repositories import ProjectRepository
from src.infrastructure.persistence.mysql.models import ProjectModel


class MySQLProjectRepository(ProjectRepository):
    """MySQL 项目仓储实现"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ProjectModel) -> Project:
        """将 ORM 模型转换为领域实体"""
        return Project(
            id=model.id,
            name=model.name,
            description=model.description,
            industry=model.industry,
            owner_id=model.owner_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Project) -> ProjectModel:
        """将领域实体转换为 ORM 模型"""
        return ProjectModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            industry=entity.industry.value if hasattr(entity.industry, 'value') else entity.industry,
            owner_id=entity.owner_id,
        )

    async def create(self, project: Project) -> Project:
        """创建项目"""
        model = self._to_model(project)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """根据ID获取项目"""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_owner(self, owner_id: str) -> list[Project]:
        """获取用户的所有项目"""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.owner_id == owner_id)
        )
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, project: Project) -> Project:
        """更新项目"""
        result = await self.session.execute(
            select(ProjectModel).where(ProjectModel.id == project.id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.name = project.name
            model.description = project.description
            model.industry = project.industry.value if hasattr(project.industry, 'value') else project.industry
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_entity(model)
        raise ValueError(f"Project {project.id} not found")

    async def delete(self, project_id: str) -> None:
        """删除项目"""
        await self.session.execute(
            delete(ProjectModel).where(ProjectModel.id == project_id)
        )
        await self.session.commit()
