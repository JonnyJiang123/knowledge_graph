from __future__ import annotations

from typing import Any

from src.application.commands.create_entity import CreateEntityCommand
from src.application.commands.create_graph_project import CreateGraphProjectCommand
from src.application.commands.create_relation import CreateRelationCommand
from src.application.queries.list_neighbors import ListNeighborsQuery
from src.domain.entities.entity import Entity
from src.domain.entities.graph_project import GraphProject
from src.domain.entities.relation import Relation
from src.domain.ports.repositories import GraphEntityRepository, GraphProjectRepository


class GraphServiceError(Exception):
    """Base error for graph service failures."""


class GraphProjectNotFoundError(GraphServiceError):
    def __init__(self, project_id: str) -> None:
        super().__init__(f"Graph project {project_id} not found")
        self.project_id = project_id


class GraphProjectAccessError(GraphServiceError):
    def __init__(self, project_id: str) -> None:
        super().__init__(f"You do not have access to project {project_id}")
        self.project_id = project_id


class GraphService:
    def __init__(
        self,
        graph_project_repo: GraphProjectRepository,
        graph_entity_repo: GraphEntityRepository,
    ) -> None:
        self._graph_project_repo = graph_project_repo
        self._graph_entity_repo = graph_entity_repo

    async def create_project(self, command: CreateGraphProjectCommand) -> GraphProject:
        project = GraphProject.new(
            name=command.name,
            owner_id=command.owner_id,
            industry=command.industry,
            description=command.description,
            metadata=command.metadata,
        )
        return await self._graph_project_repo.create(project)

    async def list_projects(self, owner_id: str) -> list[GraphProject]:
        return await self._graph_project_repo.list_by_owner(owner_id)

    async def get_project(self, project_id: str, owner_id: str) -> GraphProject:
        return await self._require_project(project_id, owner_id)

    async def create_entity(self, command: CreateEntityCommand) -> Entity:
        await self._require_project(command.project_id, command.owner_id)
        entity = Entity.create(
            project_id=command.project_id,
            external_id=command.external_id,
            type=command.type,
            labels=command.labels,
            properties=command.properties,
        )
        return await self._graph_entity_repo.merge_entity(entity)

    async def create_relation(self, command: CreateRelationCommand) -> Relation:
        await self._require_project(command.project_id, command.owner_id)
        relation = Relation.create(
            project_id=command.project_id,
            source_id=command.source_id,
            target_id=command.target_id,
            type=command.type,
            properties=command.properties,
        )
        return await self._graph_entity_repo.merge_relation(relation)

    async def list_neighbors(self, query: ListNeighborsQuery) -> dict[str, list[Any]]:
        await self._require_project(query.project_id, query.owner_id)
        depth = max(0, min(query.depth, 3))
        raw = await self._graph_entity_repo.find_neighbors(
            project_id=query.project_id,
            entity_id=query.entity_id,
            depth=depth,
        )
        limit = query.limit if query.limit and query.limit > 0 else None
        if limit:
            raw["entities"] = raw["entities"][:limit]
            raw["relations"] = raw["relations"][:limit]
        return raw

    async def _require_project(
        self,
        project_id: str,
        owner_id: str | None = None,
    ) -> GraphProject:
        project = await self._graph_project_repo.get(project_id)
        if not project:
            raise GraphProjectNotFoundError(project_id)
        if owner_id and project.owner_id != owner_id:
            raise GraphProjectAccessError(project_id)
        return project
