from django.urls import path
from . import views

urlpatterns = [
    path("", views.report),
    path("ge/report/", views.report),
    path("ge/search/", views.search, name="search"),
    path("ge/edit_fund/<int:item_id>", views.edit_fund, name="edit_fund"),
    path("ge/add_fund/", views.add_fund, name="add_fund"),
    path("ge/delete_fund/<int:item_id>", views.delete_fund, name="delete_fund"),
    path("logs/", views.show_log, name="show_log"),
    path("logs/<int:line_count>", views.show_log, name="show_log"),
    path("release_notes/", views.release_notes, name="release_notes"),
    # TODO: Change this temporary path & view name, when original report is fully replaced.
    path("ge/report_from_qdb_temp/", views.report_from_qdb_temp),
]
