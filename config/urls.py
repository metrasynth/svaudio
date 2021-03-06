from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views as flatpages_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect
from django.urls import include, path
from django.views import defaults as default_views
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from rest_framework.authtoken.views import obtain_auth_token


def favicon(request):
    return redirect(
        staticfiles_storage.url("images/favicons/favicon.ico"),
        permanent=True,
    )


urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("svaudio.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    path("activity/", include("actstream.urls")),
    path("comments/", include("django_comments.urls")),
    # Redirect to favicon
    path("favicon.ico", favicon),
    # Your stuff: custom urls includes go here
    path("", include("svaudio.artists.urls", namespace="artists")),
    path("", include("svaudio.repo.urls", namespace="repo")),
    path("", include("svaudio.tags.urls", namespace="tags")),
    path("claims/", include("svaudio.claims.urls", namespace="claims")),
    # Flatpages go last
    path("", flatpages_views.flatpage, {"url": "/"}, name="home"),
    path("about/", flatpages_views.flatpage, {"url": "/about/"}, name="about"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
    # GraphQL base url
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
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
