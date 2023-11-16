from django.urls import path
from . import views

urlpatterns = [
    path("qdb/report/", views.report),
    path("qdb/logout/", views.logoutandlogin),
    path("", views.report),
]
