from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("qdb.urls")),
    path("", include("ge.urls")),
    path("admin/", admin.site.urls),
    path("", include("django.contrib.auth.urls")),
]
