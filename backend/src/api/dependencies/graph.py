from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.graph_service import GraphService
from src.infrastructure.persistence.mysql.database import get_db
from src.infrastructure.persistence.mysql.repositories.graph_project_repository import (
    MySQLGraphProjectRepository,
)
from src.infrastructure.persistence.neo4j.graph_repository import Neo4jGraphRepository


async def get_graph_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GraphService:
    project_repo = MySQLGraphProjectRepository(db)
    entity_repo = Neo4jGraphRepository()
    return GraphService(
        graph_project_repo=project_repo,
        graph_entity_repo=entity_repo,
    )
