from django.shortcuts import render
from django.http.response import HttpResponse
from django.core.management import call_command
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
import json
from .forms import ReportForm
from django.contrib import messages
from django.utils.html import format_html
from qdb.scripts.settings import ENV


@login_required(login_url='/login/')
def report(request):
    if request.is_ajax():
        submitbutton = request.POST.get("submit")
        form = ReportForm(request.POST or None)
        if form.is_valid():
            unit = form.cleaned_data['unit'].id
            unit_name = form.cleaned_data['unit'].name
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']

            try:
                report = run_qdb_reporter(unit, month, year)
                messages.success(
                    request, 'QDB report successfully generated.', extra_tags=unit_name)
            except Exception as e:
                print(str(e))
                if 'Login failed for user' in str(e):
                    messages.error(
                        request, format_html(
                            'Remote database not available: no report could be generated.<br>-----<br>Please try again later as this may be due to routine maintenance.<br>Note: Middle-of-the-night maintenance can take up to 60 minutes'), extra_tags=unit_name)
                elif 'timed out' in str(e):
                    # apply escaping to (unsafe) html with format_html
                    messages.error(
                        request, format_html('Network problem: no report could be generated.<br>-----<br>Please use the <a href="https://www.it.ucla.edu/it-support-center/services/virtual-private-network-vpn-clients">UCLA VPN</a> when off campus.<br><a href="https://uclalibrary.github.io/research-tips/get-configured/">Help with VPN</a> (tutorials on how to connect).'), extra_tags=unit_name)
                else:
                    messages.error(
                        request, format_html('Error: no report could be generated.<br>-----<br>Please report this to the DIIT Help Desk:<br><a href="https://jira.library.ucla.edu/servicedesk/customer/portals">UCLA Library Service Portal</a>'), extra_tags=unit_name)
        else:
            messages.error(
                request, format_html('please ensure valid selections.'), extra_tags='Form error')

        # assemble and return any messages
        django_messages = []
        for message in messages.get_messages(request):
            django_messages.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            })
        data = {}
        data['messages'] = django_messages
        return HttpResponse(json.dumps(data), content_type="application/json")

    else:
        form = ReportForm()
        return render(request, 'form.html', {'form': form})


def run_qdb_reporter(unit_from_form, month_from_form, year_from_form):
    # suppress unneeded outputs in non-dev environment(s)
    if ENV != 'dev':  # pragma: no cover
        call_command('run_qdb_reporter', list_units=False, year=int(year_from_form),
                     month=int(month_from_form), units=[unit_from_form], email=True, list_recipients=False)
    # in dev, set list_units, list_recipients True for more information printed to the terminal
    else:
        # for override_recipients, set to either None or your desired email(s) ['email1@library.ucla.edu', 'email2@library.ucla.edu', ...]
        call_command('run_qdb_reporter', list_units=True, year=int(year_from_form),
                     month=int(month_from_form), units=[unit_from_form], email=False, list_recipients=True, override_recipients=None)


def logoutandlogin(request):
    return logout_then_login(request, login_url='/qdb/report/')
