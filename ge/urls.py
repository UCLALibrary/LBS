from django.urls import path
from . import views

urlpatterns = [
    path("ge/report/", views.report),
    path("", views.report),
]
