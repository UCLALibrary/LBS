from django.urls import path
from . import views

urlpatterns = [
    path("qdb/report/", views.report),
    path("qdb/logout/", views.logoutandlogin),
    path("qdb/release_notes/", views.release_notes, name="release_notes"),
    path("", views.report),
]
