from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Tuple

from src.domain.ports.repositories import PreviewCachePort


class InMemoryPreviewCache(PreviewCachePort):
    """Simple asyncio-safe preview cache for development/testing."""

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        expires_at = time.time() + ttl_seconds
        async with self._lock:
            self._store[key] = (value, expires_at)

    async def get(self, key: str) -> Any | None:
        now = time.time()
        async with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            value, expires_at = item
            if expires_at < now:
                self._store.pop(key, None)
                return None
            return value
