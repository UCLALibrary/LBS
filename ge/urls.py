from django.urls import path
from . import views

urlpatterns = [
    path("ge/report/", views.report),
    path("", views.report),
    path("logs/", views.show_log, name="show_log"),
    path("logs/<int:line_count>", views.show_log, name="show_log"),
]
