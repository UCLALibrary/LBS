from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ge.forms import ReportForm
from ge.views_utils import download_excel_file, download_zip_file


# TODO: Clean up auth system across qdb/ge apps
@login_required(login_url="/login/")
def report(request: HttpRequest) -> HttpResponse:
    context = {}  # default, for final render
    if request.method == "POST":
        # Make sure report_form is initialized, for later use.
        report_form = ReportForm()

    if request.method == "GET":
        report_form = ReportForm(request.GET)
        if report_form.is_valid():
            report_type = request.GET.get("report_type", "")
            ledger_year_month = request.GET.get("ledger_year_month", "")
            if "report_submit" in request.GET:
                return download_excel_file(report_type, ledger_year_month)
            elif "download_zip_submit" in request.GET:
                return download_zip_file(ledger_year_month)
        else:
            report_form = ReportForm()
            context = {"report_form": report_form}

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
def release_notes(request: HttpRequest) -> HttpResponse:
    return render(request, "ge/release_notes.html")
