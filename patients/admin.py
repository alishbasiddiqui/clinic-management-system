from django.contrib import admin
from .models import Patient, Payment, DoctorAssignment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "patient_code",
        "name",
        "gender",
        "age",
        "is_emergency",
        "registered_at",
    )
    search_fields = ("name",)
    list_filter = ("gender", "is_emergency")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "amount",
        "payment_method",
        "payment_status",
        "payment_date",
    )
    list_filter = ("payment_method", "payment_status")


@admin.register(DoctorAssignment)
class DoctorAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "doctor_type",
        "assigned_at",
    )
    list_filter = ("doctor_type",)