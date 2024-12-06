from django import forms
from .models import Unit, CronJob
import datetime

MONTHS = [
    ("1", "Jan"),
    ("2", "Feb"),
    ("3", "Mar"),
    ("4", "Apr"),
    ("5", "May"),
    ("6", "Jun"),
    ("7", "Jul"),
    ("8", "Aug"),
    ("9", "Sep"),
    ("10", "Oct"),
    ("11", "Nov"),
    ("12", "Dec"),
]
currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
month_default = 1
month_now = int(date.strftime("%m"))
year = int(date.strftime("%Y"))
year_default = year

if month_now == 1:
    month_default = 12
    year_default = year - 1
elif month_now > 1 and month_now < 13:
    month_default = month_now - 1

YEARS = [(year, year)]
for i in range(1, 3):
    YEARS.append((year - i, year - i))
YEARS = tuple(YEARS)


class ReportForm(forms.Form):
    unit = forms.ModelChoiceField(queryset=Unit.objects.all().order_by("name"))
    year = forms.ChoiceField(choices=YEARS, initial=year_default)
    month = forms.ChoiceField(choices=MONTHS, initial=month_default)
    send_email = forms.BooleanField(required=False, initial=True)
    override_recipients = forms.CharField(required=False)


class CronForm(forms.ModelForm):
    class Meta:
        model = CronJob
        fields = [
            "minutes",
            "hours",
            "days_of_month",
            "months",
            "days_of_week",
            "command",
            "enabled",
        ]
        # Default sizes are fine except for command field
        widgets = {
            "command": forms.TextInput(attrs={"size": 100}),
        }
