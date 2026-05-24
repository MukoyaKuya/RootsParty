import logging


logger = logging.getLogger(__name__)

try:
    from celery import shared_task as celery_shared_task
except ImportError:
    celery_shared_task = None


class LocalTask:
    def __init__(self, func):
        self.func = func
        self.__name__ = getattr(func, '__name__', self.__class__.__name__)
        self.__doc__ = getattr(func, '__doc__', None)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        logger.warning("Celery is not installed; running task %s synchronously.", self.__name__)
        return self.func(*args, **kwargs)

    apply_async = delay


def shared_task(*decorator_args, **decorator_kwargs):
    if celery_shared_task:
        return celery_shared_task(*decorator_args, **decorator_kwargs)

    if decorator_args and callable(decorator_args[0]) and len(decorator_args) == 1 and not decorator_kwargs:
        return LocalTask(decorator_args[0])

    def decorator(func):
        return LocalTask(func)

    return decorator
