from __future__ import annotations

from dataclasses import dataclass

from src.domain.entities.data_source import DataSource
from src.domain.ports.repositories import DataSourceRepository


@dataclass
class RegisterMySQLDataSourceCommand:
    project_id: str
    name: str
    host: str
    port: int
    database: str
    username: str
    password: str


async def register_mysql_source(
    repo: DataSourceRepository,
    command: RegisterMySQLDataSourceCommand,
) -> DataSource:
    entity = DataSource.create_mysql(
        project_id=command.project_id,
        name=command.name,
        host=command.host,
        port=command.port,
        database=command.database,
        username=command.username,
        password=command.password,
    )
    return await repo.create(entity)
