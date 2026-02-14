from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.graph import get_graph_service
from src.api.schemas.graph import (
    GraphEntityCreate,
    GraphEntityResponse,
    GraphRelationCreate,
    GraphRelationResponse,
    NeighborResponse,
)
from src.application.commands.create_entity import CreateEntityCommand
from src.application.commands.create_relation import CreateRelationCommand
from src.application.queries.list_neighbors import ListNeighborsQuery
from src.application.services.graph_service import (
    GraphProjectAccessError,
    GraphProjectNotFoundError,
    GraphService,
)
from src.domain.entities.user import User

router = APIRouter(prefix="/api/graph/projects", tags=["graph"])


def _map_graph_error(exc: Exception) -> HTTPException:
    if isinstance(exc, GraphProjectNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Graph project not found",
        )
    if isinstance(exc, GraphProjectAccessError):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this graph project",
        )
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )


@router.post(
    "/{project_id}/entities",
    response_model=GraphEntityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_graph_entity(
    project_id: str,
    payload: GraphEntityCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GraphService, Depends(get_graph_service)],
):
    command = CreateEntityCommand(
        project_id=project_id,
        owner_id=current_user.id,
        external_id=payload.external_id,
        type=payload.type,
        labels=payload.labels,
        properties=payload.properties,
    )
    try:
        entity = await service.create_entity(command)
    except Exception as exc:  # noqa: BLE001 - mapped to HTTP
        raise _map_graph_error(exc) from None
    return entity


@router.post(
    "/{project_id}/relations",
    response_model=GraphRelationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_graph_relation(
    project_id: str,
    payload: GraphRelationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GraphService, Depends(get_graph_service)],
):
    command = CreateRelationCommand(
        project_id=project_id,
        owner_id=current_user.id,
        source_id=payload.source_id,
        target_id=payload.target_id,
        type=payload.type,
        properties=payload.properties,
    )
    try:
        relation = await service.create_relation(command)
    except Exception as exc:  # noqa: BLE001 - mapped to HTTP
        raise _map_graph_error(exc) from None
    return relation


@router.get("/{project_id}/neighbors", response_model=NeighborResponse)
async def list_neighbors(
    project_id: str,
    entity_id: Annotated[str, Query(..., description="Start entity id")],
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[GraphService, Depends(get_graph_service)],
    depth: int = Query(1, ge=0, le=3),
    limit: int | None = Query(default=None, gt=0),
):
    query = ListNeighborsQuery(
        project_id=project_id,
        owner_id=current_user.id,
        entity_id=entity_id,
        depth=depth,
        limit=limit,
    )
    try:
        neighbors = await service.list_neighbors(query)
    except Exception as exc:  # noqa: BLE001 - mapped to HTTP
        raise _map_graph_error(exc) from None
    return NeighborResponse(
        entities=neighbors["entities"],
        relations=neighbors["relations"],
    )
