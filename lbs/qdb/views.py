from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ReportForm


def report(request):
    form = ReportForm()
    return render(request, 'form.html', {'form': form})
    # return HttpResponse('report view')
