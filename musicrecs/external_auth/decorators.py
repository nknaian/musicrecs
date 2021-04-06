from functools import wraps

from flask import session

from .exceptions import ExternalAuthFailure


def retry_after_auth():
    """Save information about the function call, such that
    it can be retried after authentication is complete
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Run the wrapped function
            try:
                return func(*args, **kwargs)
            # Save the function information and re-raise exception
            except ExternalAuthFailure as e:
                session["external_auth_retry_func_info"] = {
                    "qualname": func.__qualname__,
                    "module": func.__module__,
                    "args": args,
                    "kwargs": kwargs
                }
                raise e
        return decorated_function
    return decorator
