from django.shortcuts import render


def error_404(request, exception=None):  # page_not_found_view
    return render(request, 'handlers/404.html', status=404)


def error_500(request, exception=None):  # error_view
    return render(request, 'handlers/500.html', status=500)


def error_403(request, exception=None):  # permission_denied_view
    return render(request, 'handlers/403.html', status=403)


def error_400(request, exception=None):  # bad_request_view
    return render(request, 'handlers/400.html', status=400)
