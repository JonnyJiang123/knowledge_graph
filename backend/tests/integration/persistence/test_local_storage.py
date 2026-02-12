import pytest
from uuid import uuid4

from src.domain.value_objects.ingestion import FileArtifact, FileFormat
from src.infrastructure.storage.local_storage import LocalFileStorage


@pytest.mark.asyncio
async def test_save_and_delete_file(tmp_path):
    storage = LocalFileStorage(base_dir=tmp_path)
    artifact = FileArtifact(
        artifact_id=str(uuid4()),
        project_id="proj-1",
        stored_path="proj-1/raw/data.csv",
        file_format=FileFormat.CSV,
        size_bytes=12,
        uploaded_by="user-1",
    )

    await storage.save(artifact, b"test-data")
    full_path = tmp_path / "proj-1" / "raw" / "data.csv"
    assert full_path.exists()

    await storage.delete(artifact.stored_path)
    assert not full_path.exists()
