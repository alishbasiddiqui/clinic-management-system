from django import forms

from .models import Patient


class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ("patient_id", "name", "age", "gender", "problem", "priority")
        widgets = {
            "problem": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "patient_id": "Patient ID",
            "name": "Full name",
            "problem": "Reported problem",
        }
