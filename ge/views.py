from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ge.forms import ExcelUploadForm
from ge.models import BFSImport, CDWImport, MTFImport
from ge.views_utils import add_funds, import_excel_data, update_data


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
