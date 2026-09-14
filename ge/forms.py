from django import forms


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
            ("aul_grappone", "AUL Grappone"),
        ],
        widget=forms.Select(),
    )
    # TODO: Fill this out
    ledger_year_month = forms.ChoiceField(
        label="Month:", choices=[("202607", "202607")]
    )
