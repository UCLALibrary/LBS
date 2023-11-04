from django import forms

from ge.models import LibraryData


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


class LibraryDataSearchForm(forms.Form):
    search_types = [
        ("fund", "Fund"),
        ("keyword", "Title / Notes"),
    ]
    search_type = forms.ChoiceField(choices=search_types, initial="fund")
    search_term = forms.CharField(label="Search for")


class LibraryDataEditForm(forms.ModelForm):
    class Meta:
        model = LibraryData
        exclude = ["unit_grande", "new_fund"]
        # Default ModelForm CharField display sizes are mostly inadequate.
        widgets = {
            # Multi-line textareas
            "fund_purpose": forms.Textarea(attrs={"cols": 80, "rows": 2}),
            "fund_restriction": forms.Textarea(attrs={"cols": 80, "rows": 2}),
            "fund_summary": forms.Textarea(attrs={"cols": 80, "rows": 2}),
            "lbs_notes": forms.Textarea(attrs={"cols": 80, "rows": 2}),
            "notes": forms.Textarea(attrs={"cols": 80, "rows": 2}),
            # Wider single-line text fields
            "fund_title": forms.TextInput(attrs={"size": 80}),
        }


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
