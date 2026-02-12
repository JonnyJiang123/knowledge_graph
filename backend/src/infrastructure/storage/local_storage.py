from __future__ import annotations

from pathlib import Path

import aiofiles

from src.config import settings
from src.domain.ports.repositories import FileStoragePort
from src.domain.value_objects.ingestion import FileArtifact


class LocalFileStorage(FileStoragePort):
    """Simple filesystem-backed storage for uploaded artifacts."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = Path(base_dir or settings.upload_base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _full_path(self, stored_path: str) -> Path:
        path = Path(stored_path)
        if not path.is_absolute():
            path = self.base_dir / path
        return path

    async def save(self, artifact: FileArtifact, data: bytes) -> FileArtifact:
        full_path = self._full_path(artifact.stored_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as stream:
            await stream.write(data)

        return artifact

    async def delete(self, stored_path: str) -> None:
        full_path = self._full_path(stored_path)
        if full_path.exists():
            full_path.unlink()
