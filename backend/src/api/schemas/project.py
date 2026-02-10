from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.value_objects.industry import Industry


class ProjectCreate(BaseModel):
    """项目创建请求"""
    name: str
    description: Optional[str] = None
    industry: Industry


class ProjectUpdate(BaseModel):
    """项目更新请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[Industry] = None


class ProjectResponse(BaseModel):
    """项目响应"""
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
    """项目列表响应"""
    items: list[ProjectResponse]
    total: int
