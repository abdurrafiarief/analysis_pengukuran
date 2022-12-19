from django import forms
from .models import Measurements, Part

class MeasurementsForm(forms.ModelForm):
    class Meta:
        model = Measurements
        fields = ["part_id", "part_name",
                 "length_units", "control",
                 "nom", "measurement", 
                 "tolerance", "deviation",
                  "test_result", 
                  "out_of_tolerance", "upload_time"]

class CSVFileForm(forms.Form):
    file = forms.FileField()

class ExcelFileForm(forms.Form):
    excel_file = forms.FileField()

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['part_id', 'excel_file']