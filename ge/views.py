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
            import_excel_data(bfs_file, BFSImport)
            cdw_file = request.FILES["cdw_filename"]
            import_excel_data(cdw_file, CDWImport)
            mtf_file = request.FILES["mtf_filename"]
            import_excel_data(mtf_file, MTFImport)

    else:
        form = ExcelUploadForm()
    context = {"form": form}
    return render(request, "ge/ge_report.html", context)
