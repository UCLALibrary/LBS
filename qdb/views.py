import json
import logging
from django.http import HttpRequest
from django.shortcuts import render
from django.http.response import HttpResponse
from django.core.management import call_command
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from .forms import ReportForm
from django.contrib import messages
from django.utils.html import format_html
from qdb.scripts.settings import ENV

logger = logging.getLogger(__name__)


@login_required(login_url="/login/")
def report(request: HttpRequest) -> HttpResponse:
    # This was originally "if request.is_ajax()"... which was deprecated
    # with Django 3.1, removed in 4.0.
    # For now I'm going with the equivalent, per
    # https://docs.djangoproject.com/en/3.1/ref/request-response/#django.http.HttpRequest.is_ajax
    # TODO: Is this ajax check really needed?
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # TODO: submitbutton is never used explicitly; why is "submit" checked here?
        submitbutton = request.POST.get("submit")
        form = ReportForm(request.POST or None)
        if form.is_valid():
            unit = form.cleaned_data["unit"].id
            unit_name = form.cleaned_data["unit"].name
            year = form.cleaned_data["year"]
            month = form.cleaned_data["month"]
            send_email = form.cleaned_data["send_email"]
            override_recipients = form.cleaned_data["override_recipients"]
            # Comes through as empty string if no value set
            if override_recipients == "":
                override_recipients = None
            else:
                # Convert to list by splitting on space between addresses, if present
                override_recipients = override_recipients.split()

            try:
                run_qdb_reporter(unit, month, year, send_email, override_recipients)
                messages.success(
                    request, "QDB report successfully generated.", extra_tags=unit_name
                )
            except Exception as e:
                exception_message = str(e)
                logger.error(exception_message)
                if "Login failed for user" in exception_message:
                    messages.error(
                        request,
                        format_html(
                            "Remote database not available: no report could be generated."
                            "<br>-----"
                            "<br>Please try again later as this may be due to routine maintenance."
                            "<br>Note: Middle-of-the-night maintenance can take up to 60 minutes"
                        ),
                        extra_tags=unit_name,
                    )
                elif "timed out" in exception_message:
                    # apply escaping to (unsafe) html with format_html
                    messages.error(
                        request,
                        format_html(
                            "Network problem: no report could be generated."
                            "<br>-----"
                            "<br>Please use the <a href='https://www.it.ucla.edu/it-support-center/services/virtual-private-network-vpn-clients'>UCLA VPN</a> when off campus."
                            "<br><a href='https://uclalibrary.github.io/research-tips/get-configured/'>Help with VPN</a> (tutorials on how to connect)."
                        ),
                        extra_tags=unit_name,
                    )
                else:
                    messages.error(
                        request,
                        format_html(
                            "Error: no report could be generated."
                            "<br>-----"
                            "<br>Please report this to the DIIT Help Desk:"
                            "<br><a href='https://uclalibrary.atlassian.net/servicedesk/customer/portals'>"
                            "UCLA Library Service Portal</a>"
                        ),
                        extra_tags=unit_name,
                    )
        else:
            messages.error(
                request,
                format_html("please ensure valid selections."),
                extra_tags="Form error",
            )

        # assemble and return any messages
        django_messages = []
        for message in messages.get_messages(request):
            django_messages.append(
                {
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags,
                }
            )
        data = {}
        data["messages"] = django_messages
        return HttpResponse(json.dumps(data), content_type="application/json")

    else:
        form = ReportForm()
        # Inclue ENV for possible dev/test/prod conditional display of form fields.
        return render(request, "form.html", {"form": form, "ENV": ENV})


def run_qdb_reporter(
    unit_from_form, month_from_form, year_from_form, send_email, override_recipients
):
    # Suppress unit debugging list in non-dev environment.
    # list_recipients is useful, leave it on.
    if ENV != "dev":
        list_units = False
    else:
        list_units = True
    # Run the report, send it by email if appropriate
    call_command(
        "run_qdb_reporter",
        list_units=list_units,
        year=int(year_from_form),
        month=int(month_from_form),
        units=[unit_from_form],
        email=send_email,
        list_recipients=True,
        override_recipients=override_recipients,
    )


def logoutandlogin(request):
    return logout_then_login(request)
