from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.domain.value_objects.industry import Industry


class ProjectCreate(BaseModel):
    """椤圭洰鍒涘缓璇锋眰"""
    name: str
    description: Optional[str] = None
    industry: Industry


class ProjectUpdate(BaseModel):
    """椤圭洰鏇存柊璇锋眰"""
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[Industry] = None


class ProjectResponse(BaseModel):
    """椤圭洰鍝嶅簲"""
    id: str
    name: str
    description: Optional[str]
    industry: Industry
    owner_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """椤圭洰鍒楄〃鍝嶅簲"""
    items: list[ProjectResponse]
    total: int


class GraphProjectCreate(BaseModel):
    name: str
    industry: Industry
    description: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class GraphProjectResponse(BaseModel):
    id: str
    name: str
    industry: Industry
    status: str
    owner_id: str
    description: Optional[str]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class GraphProjectListResponse(BaseModel):
    items: list[GraphProjectResponse]
    total: int
