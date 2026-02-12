from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.domain.entities.data_source import DataSource
from src.domain.ports.repositories import DataSourceRepository
from src.domain.value_objects.ingestion import DataSourceType
from src.infrastructure.persistence.mysql.models import DataSourceModel


class MySQLDataSourceRepository(DataSourceRepository):
    """MySQL implementation of the DataSource repository."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._fernet = Fernet(settings.encryption_key.encode())

    def _encode_config(self, entity: DataSource) -> dict[str, Any]:
        config = dict(entity.config)
        if entity.type == DataSourceType.MYSQL and "password" in config:
            password = config["password"]
            if password is not None:
                config["password"] = self._fernet.encrypt(password.encode()).decode()
        return config

    def _decode_config(self, type_value: str, config: Optional[dict[str, Any]]) -> dict[str, Any]:
        data = dict(config or {})
        if type_value == DataSourceType.MYSQL.value and data.get("password"):
            try:
                decrypted = self._fernet.decrypt(data["password"].encode()).decode()
                data["password"] = decrypted
            except Exception:
                # If decryption fails, keep the stored value to avoid data loss.
                pass
        return data

    def _to_entity(self, model: DataSourceModel) -> DataSource:
        config = self._decode_config(model.type, model.config)
        return DataSource(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            type=DataSourceType(model.type),
            config=config,
            status=model.status,
            last_used_at=model.last_used_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: DataSource) -> DataSourceModel:
        encoded_config = self._encode_config(entity)
        return DataSourceModel(
            id=entity.id or str(uuid4()),
            project_id=entity.project_id,
            name=entity.name,
            type=entity.type.value,
            status=entity.status,
            config=encoded_config,
            last_used_at=entity.last_used_at,
        )

    async def create(self, source: DataSource) -> DataSource:
        model = self._to_model(source)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def update(self, source: DataSource) -> DataSource:
        model = await self.session.get(DataSourceModel, source.id)
        if model is None:
            raise ValueError(f"Data source {source.id} not found")

        model.name = source.name
        model.status = source.status
        model.config = self._encode_config(source)
        model.last_used_at = source.last_used_at
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_entity(model)

    async def list(self, project_id: str) -> list[DataSource]:
        result = await self.session.execute(
            select(DataSourceModel)
            .where(DataSourceModel.project_id == project_id)
            .order_by(DataSourceModel.created_at.desc())
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def get(self, source_id: str) -> Optional[DataSource]:
        model = await self.session.get(DataSourceModel, source_id)
        return self._to_entity(model) if model else None
