"""
Structured logging utilities for the Roots Party platform.
Provides consistent logging across the application with context and metadata.
"""
import logging
import sys
from functools import wraps
from django.conf import settings

# Configure root logger
logger = logging.getLogger('rootsparty')
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

# Console handler for development
if settings.DEBUG:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Google Cloud Logging handler for production
if not settings.DEBUG and hasattr(settings, 'GOOGLE_CLOUD_PROJECT'):
    try:
        import google.cloud.logging
        client = google.cloud.logging.Client()
        client.setup_logging()
        # Google Cloud Logging is automatically configured
    except ImportError:
        logger.warning("Google Cloud Logging not available")


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): Logger name (typically __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(f'rootsparty.{name}')


def log_request(view_func):
    """
    Decorator to log HTTP requests with metadata.
    
    Usage:
        @log_request
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        logger = get_logger('requests')
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Log request
        logger.info(
            f"{request.method} {request.path}",
            extra={
                'ip': ip,
                'user': request.user.username if request.user.is_authenticated else 'anonymous',
                'method': request.method,
                'path': request.path,
            }
        )
        
        try:
            response = view_func(request, *args, **kwargs)
            
            # Log response
            logger.debug(
                f"{request.method} {request.path} - {response.status_code}",
                extra={
                    'status_code': response.status_code,
                    'ip': ip,
                }
            )
            
            return response
        except Exception as e:
            logger.error(
                f"Error in {request.method} {request.path}: {str(e)}",
                extra={
                    'ip': ip,
                    'error': str(e),
                    'exception_type': type(e).__name__,
                },
                exc_info=True
            )
            raise
    
    return wrapper


def log_model_action(action, model_name, instance_id=None, user=None, **kwargs):
    """
    Log model actions (create, update, delete).
    
    Args:
        action (str): Action type ('create', 'update', 'delete')
        model_name (str): Model name
        instance_id: Instance ID
        user: User performing the action
        **kwargs: Additional metadata
    """
    logger = get_logger('models')
    
    log_data = {
        'action': action,
        'model': model_name,
        'instance_id': instance_id,
        'user': user.username if user and hasattr(user, 'username') else str(user),
    }
    log_data.update(kwargs)
    
    logger.info(
        f"{action.upper()} {model_name}",
        extra=log_data
    )


def log_api_request(viewset_or_view, action, user=None, **kwargs):
    """
    Log API requests.
    
    Args:
        viewset_or_view: ViewSet or view class name
        action (str): API action
        user: User making the request
        **kwargs: Additional metadata
    """
    logger = get_logger('api')
    
    log_data = {
        'view': str(viewset_or_view),
        'action': action,
        'user': user.username if user and hasattr(user, 'username') else 'anonymous',
    }
    log_data.update(kwargs)
    
    logger.info(
        f"API {action} on {viewset_or_view}",
        extra=log_data
    )


def log_error(error, context=None, exc_info=False):
    """
    Log errors with context.
    
    Args:
        error: Exception instance or error message
        context (dict): Additional context
        exc_info (bool): Include exception traceback
    """
    logger = get_logger('errors')
    
    error_data = {
        'error': str(error),
        'error_type': type(error).__name__ if hasattr(error, '__class__') else 'Unknown',
    }
    
    if context:
        error_data.update(context)
    
    logger.error(
        f"Error: {str(error)}",
        extra=error_data,
        exc_info=exc_info
    )
