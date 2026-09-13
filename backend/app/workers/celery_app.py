"""
NETRYX EVIDENCE — Celery Worker Configuration
Async task queue for evidence processing, analysis, IOC extraction, and correlation.
"""

from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "netryx_evidence",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Worker settings
    worker_prefetch_multiplier=1,  # Fair dispatch
    worker_max_tasks_per_child=100,  # Prevent memory leaks
    worker_concurrency=4,

    # Task routing
    task_routes={
        "app.workers.evidence_processor.*": {"queue": "evidence"},
        "app.workers.analysis_worker.*": {"queue": "analysis"},
        "app.workers.ioc_worker.*": {"queue": "ioc"},
        "app.workers.correlation_worker.*": {"queue": "correlation"},
        "app.workers.embedding_worker.*": {"queue": "embedding"},
        "app.workers.report_worker.*": {"queue": "reports"},
    },

    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Result settings
    result_expires=3600,  # 1 hour
)

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "app.workers",
])
