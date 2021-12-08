
from django import forms
from .models import Unit
import datetime
MONTHS = [
    ('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7',
                                                                                         'Jul'), ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec'),
]
currentDateTime = datetime.datetime.now()
date = currentDateTime.date()
year = int(date.strftime("%Y"))
YEARS = [(year, year)]
for i in range(1, 11):
    YEARS.append((year-i, year-i))
YEARS = tuple(YEARS)


class ReportForm(forms.Form):
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all().order_by('name'), initial=1)
    year = forms.ChoiceField(
        choices=YEARS)
    month = forms.ChoiceField(
        choices=MONTHS)
