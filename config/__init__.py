# Only load Celery when running as a worker/beat - avoids import overhead for web workers (cold start)
import sys
if any(cmd in sys.argv for cmd in ('worker', 'beat', 'flower', 'multi')):
    from .celery import app as celery_app
    __all__ = ('celery_app',)
else:
    celery_app = None
    __all__ = ()
