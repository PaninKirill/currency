from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from settings import handler_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    path('account/', include('account.urls')),
    path('rate/', include('rate.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)),
                   url(r'^api-auth/', include('rest_framework.urls'))
                   ] + urlpatterns

# Custom error pages
handler404 = handler_views.error_404
handler500 = handler_views.error_500
handler403 = handler_views.error_403
handler400 = handler_views.error_400
