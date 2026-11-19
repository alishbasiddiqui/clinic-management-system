from django.contrib import admin
from .models import Patient, Prescription, Visit


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 0


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("token", "name", "doctor", "priority", "status")
    list_filter = ("doctor", "priority", "status")
    search_fields = ("name", "patient_id")
    inlines = [PrescriptionInline]


admin.site.register(Visit)
