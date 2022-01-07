from django.shortcuts import render
from django.http.response import HttpResponse
from django.core.management import call_command
from django.contrib.auth.decorators import login_required
import os
from .models import Unit
from .forms import ReportForm


@login_required
def report(request):
    request.user
    if request.method == 'POST':
        submitbutton = request.POST.get("submit")
        form = ReportForm(request.POST or None)
        if form.is_valid():
            unit = form.cleaned_data['unit'].id
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            report = run_qdb_reporter(unit, month, year)

        context = {'form': form, 'unit': unit, 'month': month,
                   'year': year, 'submitbutton': submitbutton}

        return render(request, 'form.html', user, context)
    else:
        form = ReportForm()
        return render(request, 'form.html', {'form': form})


def run_qdb_reporter(unit_from_form, month_from_form, year_from_form):
    call_command('run_qdb_reporter', year=int(year_from_form),
                 month=int(month_from_form), units=[unit_from_form])
    # append , list_units=True for testing
