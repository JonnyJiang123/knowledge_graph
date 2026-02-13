from __future__ import annotations

from celery import Celery

from src.config import settings

celery_app = Celery("knowledge_graph")
celery_app.conf.update(
    broker_url=settings.redis_uri,
    result_backend=settings.redis_uri,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_default_queue="ingestion",
    worker_send_task_events=True,
)
celery_app.autodiscover_tasks(["src.infrastructure.queue.tasks"])

__all__ = ["celery_app"]
