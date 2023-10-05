from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ge.forms import ExcelUploadForm
from ge.models import BFSImport, CDWImport, MTFImport
from ge.views_utils import import_excel_data


@login_required
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
            except KeyError as ex:
                # Exception re-raised from import_excel_data has useful info already.
                messages.error(request, ex)
    else:
        form = ExcelUploadForm()
    context = {"form": form}
    return render(request, "ge/ge_report.html", context)
