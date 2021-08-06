from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import RedirectView
from rest_framework.authtoken.views import obtain_auth_token

from democracy import __version__
from democracy.users.views import confirm_email_view


def version_view(request):
    """Prints data so those viewing the heroku endpoint don't 404 it."""
    return JsonResponse(
        {
            "name": "Democracy",
            "author": "Small Minds (smallminds.dev)",
            "api_version": str(__version__),
        }
    )


urlpatterns = [
    path("", version_view),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("django.contrib.auth.urls")),
    # User management
    path("users/", include("democracy.users.urls", namespace="users")),
    path("elections/", include("democracy.elections.urls", namespace="elections")),
    path("accounts/", include("allauth.urls")),
    path("alive/", include("democracy.alive.urls")),
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/images/favicons/favicon.ico", permanent=True),
        name="favicon",
    ),
    # Your stuff: custom urls includes go here
    path("jwt-auth/", include("democracy.reactauth.urls", namespace="reactauth")),
    path("rest-auth/", include("rest_auth.urls")),
    path(
        "rest-auth/registration/account-confirm-email/<str:key>/",
        confirm_email_view,
        name="account_confirm_email",
    ),
    path("rest-auth/registration/", include("rest_auth.registration.urls")),
    path(
        "robots.txt",
        lambda x: HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain"),
        name="robots_file",
    ),
    path("", include("democracy.swagger.urls", namespace="swagger")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
