from django import forms
from datetime import datetime
from ge.models import GeFund


def get_year_month_choices() -> list[tuple[str, str]]:
    # QAD for now; reports have been quarterly.
    # If more flexibility is needed, see qdb.forms.py implementation.

    year_month_choices: list[tuple[str, str]] = []
    today = datetime.now()
    current_year = int(today.strftime("%Y"))
    # Combine year & month, in reverse chronological order.
    # Use months which reflect ends of fiscal quarters.
    months = ["03", "06", "09", "12"]
    months.reverse()
    # Current and previous 2 calendar years.
    for year in range(current_year, current_year - 3, -1):
        for month in months:
            year_month = f"{year}{month}"
            # Don't include future year/months.
            if datetime.strptime(year_month, "%Y%m") <= today:
                year_month_choices.append((year_month, year_month))

    return year_month_choices


class ReportForm(forms.Form):
    report_type = forms.ChoiceField(
        label="Report Type:",
        # Previous coding for human entered variable values is no longer needed.
        # Now (2026), use values derived from active funds, so this list of form choices
        # is dynamic based on data maintained by LBS.
        choices=[
            (unit_name, unit_name)
            for unit_name in sorted(
                set([r.unit.name for r in GeFund.objects.filter(active=True)])
            )
        ],
        widget=forms.Select(),
    )

    ledger_year_month = forms.ChoiceField(
        label="Month:", choices=get_year_month_choices()
    )
