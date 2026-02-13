from __future__ import annotations

from typing import Any

from celery import Celery

from src.domain.ports.repositories import TaskQueuePort


class CeleryTaskQueue(TaskQueuePort):
    """Task queue adapter that delegates to Celery."""

    def __init__(self, celery_app: Celery) -> None:
        self._celery = celery_app

    async def enqueue(self, task_name: str, payload: dict[str, Any]) -> str:
        result = self._celery.send_task(task_name, kwargs=payload)
        return result.id
