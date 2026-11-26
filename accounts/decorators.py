from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*allowed_roles):
    """Login required AND the user's role must be one of allowed_roles."""

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "You don't have access to that page.")
                return redirect("dashboard")  
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
