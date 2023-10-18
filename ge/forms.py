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
