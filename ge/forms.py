from django import forms


class ExcelUploadForm(forms.Form):
    bfs_filename = forms.FileField(
        label="BFS File:",
        help_text="Data from UCLA Business and Finance Solutions",
        widget=forms.FileInput(),
    )
    cdw_filename = forms.FileField(
        label="CDW File:",
        help_text="Data from UCLA Campus Data Warehouse",
        widget=forms.FileInput(),
    )
    mtf_filename = forms.FileField(
        label="MTF File:",
        help_text="Data from UCLA Monetary Transfer Form system",
        widget=forms.FileInput(),
    )


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
            ("aul_consales", "AUL Consales"),
            ("aul_grappone", "AUL Grappone"),
        ],
        widget=forms.Select(),
    )
