import time
from functools import wraps

from rest_framework.exceptions import PermissionDenied


def has_permission(function):
    @wraps(function)
    def wrap(cls, *args, **kwargs):
        stime = time.time()

        if hasattr(cls,'request') and hasattr(cls.request,'user'):
            if str(cls.request.user) == "AnonymousUser":
                raise PermissionDenied

            return function(cls, *args, **kwargs)
        else:
            return function(cls, *args, **kwargs)

    return wrap

def has_admin_permission(function):
    @wraps(function)
    def wrap(cls, *args, **kwargs):
        stime = time.time()

        if hasattr(cls,'request') and hasattr(cls.request, 'user'):
            if str(cls.request.user) == "AnonymousUser":
                raise PermissionDenied

            if cls.request.user.is_admin != True:
                raise PermissionDenied

            return function(cls, *args, **kwargs)
        else:
            return function(cls, *args, **kwargs)

    return wrap

def has_store_permission(function):
    @wraps(function)
    def wrap(cls, *args, **kwargs):
        stime = time.time()

        if hasattr(cls,'request') and hasattr(cls.request, 'user'):
            if str(cls.request.user) == "AnonymousUser":
                raise PermissionDenied

            if cls.request.user.is_store != True:
                raise PermissionDenied

            return function(cls, *args, **kwargs)
        else:
            return function(cls, *args, **kwargs)

    return wrap

def has_customer_permission(function):
    @wraps(function)
    def wrap(cls, *args, **kwargs):
        stime = time.time()

        if hasattr(cls,'request') and hasattr(cls.request, 'user'):
            if str(cls.request.user) == "AnonymousUser":
                raise PermissionDenied

            if cls.request.user.is_customer != True:
                raise PermissionDenied

            return function(cls, *args, **kwargs)
        else:
            return function(cls, *args, **kwargs)

    return wrap