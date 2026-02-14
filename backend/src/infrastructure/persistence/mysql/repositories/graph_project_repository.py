from __future__ import annotations

from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.graph_project import GraphProject
from src.domain.ports.repositories import GraphProjectRepository
from src.infrastructure.persistence.mysql.models import GraphProjectModel


class MySQLGraphProjectRepository(GraphProjectRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: GraphProjectModel) -> GraphProject:
        return GraphProject(
            id=model.id,
            name=model.name,
            owner_id=model.owner_id,
            industry=model.industry,
            status=model.status,
            description=model.description,
            metadata=model.metadata_json or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: GraphProject) -> GraphProjectModel:
        return GraphProjectModel(
            id=entity.id,
            name=entity.name,
            owner_id=entity.owner_id,
            industry=entity.industry.value if hasattr(entity.industry, "value") else entity.industry,
            status=entity.status,
            description=entity.description,
            metadata_json=entity.metadata,
        )

    async def create(self, project: GraphProject) -> GraphProject:
        model = self._to_model(project)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def get(self, project_id: str) -> Optional[GraphProject]:
        result = await self.session.execute(
            select(GraphProjectModel).where(GraphProjectModel.id == project_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_owner(self, owner_id: str) -> list[GraphProject]:
        result = await self.session.execute(
            select(GraphProjectModel).where(GraphProjectModel.owner_id == owner_id)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def update_status(self, project_id: str, status: str) -> None:
        await self.session.execute(
            update(GraphProjectModel)
            .where(GraphProjectModel.id == project_id)
            .values(status=status)
        )
        await self.session.commit()
