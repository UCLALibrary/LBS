from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ReportForm
from django.core.management import call_command
from django.contrib.auth.decorators import login_required
import os
from .models import Unit


def report(request):
    objectlist = Unit.objects.values('name').distinct().order_by('name')
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            ###objectlist = Unit.objects.distinct('name')
            unit = form.cleaned_data['unit']
            date = form.cleaned_data['date']
            ###print(unit, date)
            report = run_qdb_reporter(unit)

    form = ReportForm()
    return render(request, 'form.html', {'form': form, 'objectlist': objectlist})
    # return HttpResponse('report view')


def run_qdb_reporter(unit_from_form):
    print(unit_from_form)

    ###make_option('-l', dest='l', action='store_true', help='list units')

    print(os.environ['QDB_DB_PASSWORD'])

    ###call_command('run_qdb_reporter', list_units=True)
    call_command('run_qdb_reporter', year=2021,
                 month=5, units=[6], list_units=True)
    ###call_command('artifact_db_loader', 'artefacts', tzsub=True, e=True)

    # return subprocess.run(['python', 'qdb/management/commands/run_qdb_reporter.py', unit_from_form], shell=False, timeout=1800)
    # return subprocess.run(['python', 'windows_path_like_D:\\path_to_script\\prog17.py', post_from_form], shell=False, timeout=1800)
