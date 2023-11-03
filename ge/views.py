from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ge.forms import ExcelUploadForm
from ge.models import BFSImport, CDWImport, MTFImport
from ge.views_utils import (
    add_funds,
    import_excel_data,
    update_data,
    create_excel_output,
)


# TODO: Clean up auth system across qdb/ge apps
@login_required(login_url="/login/")
def report(request: HttpRequest):
    print(request.GET)
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
                add_funds()
                update_data()

            except KeyError as ex:
                # Exception re-raised from import_excel_data has useful info already.
                messages.error(request, ex)

    elif request.GET.get("get_master_report"):
        return create_excel_output("master")
    elif request.GET.get("get_aul_reports"):
        return create_excel_output("aul")
    elif request.GET.get("get_dept_reports"):
        return create_excel_output("dept")
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
