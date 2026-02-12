import pytest
from datetime import UTC, datetime
from uuid import uuid4

from src.domain.entities.data_source import DataSource
from src.domain.entities.project import Project
from src.domain.value_objects.ingestion import DataSourceType, FileFormat
from src.infrastructure.persistence.mysql.repositories.data_source_repository import (
    MySQLDataSourceRepository,
)


@pytest.mark.asyncio
async def test_create_and_fetch_mysql_source(
    project: Project,
    data_source_repo: MySQLDataSourceRepository,
):
    source = DataSource.create_mysql(
        project_id=project.id,
        name="CRM",
        host="localhost",
        port=3306,
        database="crm",
        username="crm_user",
        password="secret",
    )
    source.id = str(uuid4())

    created = await data_source_repo.create(source)
    assert created.config["password"] == "secret"

    fetched = await data_source_repo.get(created.id)
    assert fetched is not None
    assert fetched.config["password"] == "secret"


@pytest.mark.asyncio
async def test_list_data_sources(
    project: Project,
    data_source_repo: MySQLDataSourceRepository,
):
    file_source = DataSource.create_file(
        project_id=project.id,
        name="Upload",
        file_format=FileFormat.CSV,
        original_filename="file.csv",
        stored_path=f"{project.id}/file.csv",
        size_bytes=1024,
        uploaded_by="user",
        uploaded_at=datetime.now(UTC),
    )
    file_source.id = str(uuid4())
    mysql_source = DataSource.create_mysql(
        project_id=project.id,
        name="DB",
        host="localhost",
        port=3306,
        database="db",
        username="db_user",
        password="pwd",
    )
    mysql_source.id = str(uuid4())

    await data_source_repo.create(file_source)
    await data_source_repo.create(mysql_source)

    items = await data_source_repo.list(project.id)
    assert len(items) >= 2
    types = {item.type for item in items}
    assert DataSourceType.FILE in types
    assert DataSourceType.MYSQL in types
