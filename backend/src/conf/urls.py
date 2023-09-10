from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from checker.views import file_detail, home_page, login_view, register_view

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
    ),
    public=True,
    permission_classes=(permissions.IsAdminUser,),
)

urlpatterns = [
    path("api/", include("checker.urls")),
    path("register/", register_view, name="register_view"),
    path("login/", login_view, name="login_view"),
    path("", home_page, name="home_page"),
    path("file_detail/<int:file_id>/", file_detail, name="file_detail"),
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
