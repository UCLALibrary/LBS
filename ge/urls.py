from django.urls import path
from . import views

urlpatterns = [
    path("", views.report),
    path("ge/report/", views.report),
    path("ge/search/", views.search),
    path("ge/edit/<int:item_id>", views.edit_librarydata, name="edit_librarydata"),
    path("logs/", views.show_log, name="show_log"),
    path("logs/<int:line_count>", views.show_log, name="show_log"),
    path("release_notes/", views.release_notes, name="release_notes"),
]
