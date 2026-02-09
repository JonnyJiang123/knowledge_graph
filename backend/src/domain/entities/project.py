from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.industry import Industry


@dataclass
class Project:
    """项目领域实体"""
    id: str
    name: str
    industry: Industry
    owner_id: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """初始化后处理，确保 industry 是枚举类型"""
        if isinstance(self.industry, str):
            self.industry = Industry(self.industry)
