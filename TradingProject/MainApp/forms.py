# MainApp/forms.py

from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    timeframe = forms.IntegerField()
