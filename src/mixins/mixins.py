from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404


class AuthRequiredMixin(object):
    """
    Checks if the user is authenticated. If hi is - return the
    normal dispatch. If not, redirect to login page.
    """
    login_url = settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), self.login_url)

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(object):
    """
    Checks if the user is authenticated or superuser. If he is -  return the
    normal dispatch. If not, redirect to 404/403 page.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404
        if not request.user.is_superuser:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
