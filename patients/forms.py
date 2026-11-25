
from decimal import Decimal

from django import forms

from .models import Patient, Payment, DoctorAssignment


class PatientRegistrationForm(forms.ModelForm):
    payment_amount = forms.DecimalField(
        label="Payment Amount",
        min_value=Decimal("0.01"),
        max_digits=10,
        decimal_places=2,
    )

    payment_method = forms.ChoiceField(
        label="Payment Method",
        choices=Payment.PAYMENT_METHOD_CHOICES,
    )

    payment_status = forms.ChoiceField(
        label="Payment Status",
        choices=Payment.PAYMENT_STATUS_CHOICES,
        initial="pending",
    )

    doctor_type = forms.ChoiceField(
        label="Assign Doctor",
        choices=DoctorAssignment.DOCTOR_CHOICES,
    )

    class Meta:
        model = Patient
        fields = ["name", "gender", "age", "is_emergency"]

        labels = {
            "name": "Patient Name",
            "gender": "Gender",
            "age": "Age",
            "is_emergency": "Emergency Case",
        }

        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Enter patient name"}
            ),
            "age": forms.NumberInput(
                attrs={"min": "0", "max": "120"}
            ),
        }