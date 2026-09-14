from django import forms
from datetime import datetime


def get_year_month_choices() -> list[tuple[str, str]]:
    # QAD for now; reports have been quarterly.
    # If more flexibility is needed, see qdb.forms.py implementation.

    year_month_choices: list[tuple[str, str]] = []
    today = datetime.now()
    current_year = int(today.strftime("%Y"))
    # Combine year & month, in reverse chronological order.
    months = ["01", "04", "07", "10"]
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
        choices=[
            ("master", "Master"),
            ("archives", "Archives"),
            ("arts", "Arts"),
            ("biomed", "Biomed"),
            ("digilib", "Digital Library"),
            ("eal", "East Asian Library"),
            ("ftva", "Film & TV Archive"),
            ("hsc", "History & SC Sciences"),
            ("hssd", "HSSD"),
            ("ias", "Intl & Area Studies"),
            ("lhr", "LHR"),
            ("lsc", "LSC"),
            ("management", "Management"),
            ("music", "Music"),
            ("oh", "Oral History"),
            ("pa", "Performing Arts"),
            ("powell", "Powell"),
            ("preservation", "Preservation"),
            ("sel", "SEL"),
            ("ul", "UL"),
            ("aul_benedetti", "AUL Benedetti"),
            ("aul_gomez", "AUL Gomez"),
        ],
        widget=forms.Select(),
    )

    ledger_year_month = forms.ChoiceField(
        label="Month:", choices=get_year_month_choices()
    )
