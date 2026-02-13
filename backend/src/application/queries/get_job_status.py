from __future__ import annotations

from src.domain.ports.repositories import IngestionJobRepository


async def get_job_status(
    repo: IngestionJobRepository,
    job_id: str,
):
    """Return a single ingestion job record."""
    return await repo.get(job_id)
