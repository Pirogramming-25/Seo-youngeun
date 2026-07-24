from functools import wraps
from urllib.parse import urlencode

from django.conf import settings
from django.shortcuts import redirect


def model_login_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        login_url = settings.LOGIN_URL
        query = urlencode({"next": request.get_full_path(), "required": "1"})
        return redirect(f"{login_url}?{query}")
    return wrapped
