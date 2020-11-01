from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from rest_framework import permissions

from rest_framework_simplejwt.views import TokenObtainPairView

from settings import handler_views

API_PREFIX = 'api/v1/'

schema_view = get_schema_view(
    openapi.Info(
        title="Currency-exchange API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', TemplateView.as_view(template_name='index.html'), name='index'),

    path('account/', include('account.urls')),
    path('rate/', include('rate.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # API
    path(f'{API_PREFIX}rate/', include('rate.api.urls')),
    path(f'{API_PREFIX}account/', include('account.api.urls')),
    path(f'{API_PREFIX}api-auth/', include('rest_framework.urls')),
    path(f'{API_PREFIX}token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    re_path(rf'^{API_PREFIX}swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    re_path(rf'^{API_PREFIX}swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    re_path(rf'^{API_PREFIX}redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        path('__debug__/', include(debug_toolbar.urls)),
    ])

    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))

# Custom error pages
handler404 = handler_views.error_404
handler500 = handler_views.error_500
handler403 = handler_views.error_403
handler400 = handler_views.error_400
