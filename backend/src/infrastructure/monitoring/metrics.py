"""监控指标收集"""

import time
from collections import defaultdict
from typing import Any

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST


# 定义指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

QUEUE_SIZE = Gauge(
    'queue_size',
    'Number of jobs in queue',
    ['queue_name']
)

DB_CONNECTIONS = Gauge(
    'db_connections',
    'Number of database connections',
    ['db_type']
)


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)

    def increment_counter(self, name: str, value: int = 1, labels: dict[str, str] | None = None) -> None:
        """增加计数器"""
        key = f"{name}:{labels}" if labels else name
        self._counters[key] += value

        # 同时更新Prometheus指标
        if name == "http_requests":
            REQUEST_COUNT.labels(
                method=labels.get("method", "GET"),
                endpoint=labels.get("endpoint", "/"),
                status=str(labels.get("status", 200))
            ).inc(value)

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """设置仪表盘值"""
        key = f"{name}:{labels}" if labels else name
        self._gauges[key] = value

    def record_histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """记录直方图值"""
        key = f"{name}:{labels}" if labels else name
        self._histograms[key].append(value)

        # 同时更新Prometheus指标
        if name == "request_latency":
            REQUEST_LATENCY.labels(
                method=labels.get("method", "GET"),
                endpoint=labels.get("endpoint", "/")
            ).observe(value)

    def get_metrics(self) -> dict[str, Any]:
        """获取所有指标"""
        return {
            "counters": dict(self._counters),
            "gauges": self._gauges,
            "histograms": {k: {"count": len(v), "avg": sum(v)/len(v) if v else 0}
                          for k, v in self._histograms.items()}
        }

    def get_prometheus_metrics(self) -> bytes:
        """获取Prometheus格式的指标"""
        return generate_latest()


# 全局指标收集器
metrics = MetricsCollector()


class RequestTiming:
    """请求计时上下文管理器"""

    def __init__(self, method: str, endpoint: str):
        self.method = method
        self.endpoint = endpoint
        self.start_time: float = 0

    def __enter__(self):
        self.start_time = time.time()
        ACTIVE_CONNECTIONS.inc()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        ACTIVE_CONNECTIONS.dec()

        REQUEST_LATENCY.labels(
            method=self.method,
            endpoint=self.endpoint
        ).observe(duration)

        status = 500 if exc_type else 200
        REQUEST_COUNT.labels(
            method=self.method,
            endpoint=self.endpoint,
            status=str(status)
        ).inc()
