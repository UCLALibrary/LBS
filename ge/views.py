from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ge.forms import ExcelUploadForm, LibraryDataEditForm, LibraryDataSearchForm
from ge.models import BFSImport, CDWImport, LibraryData, MTFImport
from ge.views_utils import (
    add_funds,
    get_librarydata_results,
    import_excel_data,
    update_data,
)


# TODO: Clean up auth system across qdb/ge apps
@login_required(login_url="/login/")
def report(request: HttpRequest):
    if request.method == "POST":
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            bfs_file = request.FILES["bfs_filename"]
            cdw_file = request.FILES["cdw_filename"]
            mtf_file = request.FILES["mtf_filename"]
            try:
                import_excel_data(bfs_file, BFSImport)
                import_excel_data(cdw_file, CDWImport)
                import_excel_data(mtf_file, MTFImport)
                messages.success(request, "All data was imported successfully.")
                # TODO: Separate form to generate reports?  For now, doing that automatically.
                messages.success(request, "Reports are being generated.")
                add_funds()
                update_data()
            except KeyError as ex:
                # Exception re-raised from import_excel_data has useful info already.
                messages.error(request, ex)
    else:
        form = ExcelUploadForm()
    context = {"form": form}
    return render(request, "ge/ge_report.html", context)


@login_required(login_url="/login/")
def show_log(request, line_count: int = 200) -> HttpResponse:
    log_file = "logs/application.log"
    try:
        with open(log_file, "r") as f:
            # Get just the last line_count lines in the log.
            lines = f.readlines()[-line_count:]
            # Template prints these as a single block, so join lines into one chunk.
            log_data = "".join(lines)
    except FileNotFoundError:
        log_data = f"Log file {log_file} not found"

    # TODO: Move / unify templates across ge and qdb apps
    return render(request, "ge/log.html", {"log_data": log_data})


@login_required(login_url="/login/")
def search(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = LibraryDataSearchForm(request.POST)
        if form.is_valid():
            search_type = form.cleaned_data["search_type"]
            search_term = form.cleaned_data["search_term"]
            results = get_librarydata_results(search_type, search_term)
            context = {"form": form, "results": results}
    else:
        form = LibraryDataSearchForm()
        context = {"form": form}
    return render(request, "ge/ge_search.html", context)


@login_required(login_url="/login/")
def edit_librarydata(request: HttpRequest, item_id: int) -> HttpResponse:
    # Get the record passed by id.
    # TODO: Do we need to support creating new records via form?
    record = LibraryData.objects.get(pk=item_id)
    if request.method == "POST":
        form = LibraryDataEditForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
    else:
        form = LibraryDataEditForm(instance=record)
    return render(request, "ge/edit_item.html", {"form": form})
