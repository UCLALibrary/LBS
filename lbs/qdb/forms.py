
from django import forms


class ReportForm(forms.Form):
    uni0 = forms.ChoiceField(choices=[('Unit1', 'Unit1'), ('unit2', 'Unit2')])
    unit = forms.ChoiceField(choices=[('Unit1', 'Unit1'), ('unit2', 'Unit2')])
    date = forms.DateField(label='Date for report',
                           widget=forms.SelectDateWidget)
