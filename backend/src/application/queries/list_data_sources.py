from __future__ import annotations

from src.domain.ports.repositories import DataSourceRepository


async def list_data_sources(
    repo: DataSourceRepository,
    project_id: str,
):
    """Fetch data sources and return safe summaries for API usage."""
    sources = await repo.list(project_id)
    return [source.safe_summary() for source in sources]
