# Config package init

# Ensure the Celery app is loaded when Django starts
try:
    from .celery import app as celery_app  # noqa
except Exception:
    celery_app = None

__all__ = ['celery_app']
