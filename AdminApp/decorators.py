from django.shortcuts import redirect, render
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'admin' not in request.session:
            messages.error(request, "Please login as admin!")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
