from __future__ import annotations

from typing import Any
from uuid import uuid4

from src.domain.ports.repositories import TaskQueuePort


class LocalTaskQueue(TaskQueuePort):
    """Best-effort background queue placeholder; records enqueued tasks."""

    def __init__(self) -> None:
        self._tasks: list[tuple[str, dict[str, Any]]] = []

    async def enqueue(self, task_name: str, payload: dict[str, Any]) -> str:
        task_id = str(uuid4())
        self._tasks.append((task_name, payload))
        return task_id
