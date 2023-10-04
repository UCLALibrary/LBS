from django import forms


class ExcelUploadForm(forms.Form):
    bfs_filename = forms.FileField(label="BFS File:", widget=forms.FileInput())
    cdw_filename = forms.FileField(label="CDW File:", widget=forms.FileInput())
    mtf_filename = forms.FileField(label="MTF File:", widget=forms.FileInput())
