# -*- coding: utf-8 -*-

from functools import wraps
from flask import abort
from flask.ext.login import current_user, login_required

from models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decoratored_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decoratored_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)

# 定义需要退出登陆的decorator
def logout_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated():
            abort(405)
        return f(*args, **kwargs)
    return wrapper
