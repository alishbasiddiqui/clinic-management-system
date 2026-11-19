from functools import wraps

from django.contrib import messages
from django.db import transaction
from django.db.models import Case, IntegerField, Max, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PatientRegistrationForm
from .models import Patient, Visit


def doctor_required(view):
    """Redirect to the doctor-selection page if no doctor is logged in."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        doctor = request.session.get("doctor")
        if not doctor:
            return redirect("select_doctor")
        return view(request, doctor, *args, **kwargs)
    return wrapper


def _own_patient(doctor, token):
    return get_object_or_404(Patient, token=token, doctor__iexact=doctor)


def select_doctor(request):
    doctors = list(
        Patient.objects.order_by("doctor").values_list("doctor", flat=True).distinct()
    )
    if request.method == "POST":
        name = request.POST.get("doctor", "").strip()
        if not name:
            messages.error(request, "Doctor name cannot be empty.")
        elif not Patient.objects.filter(doctor__iexact=name).exists():
            messages.error(request, "No patients are assigned to this doctor.")
        else:
            # keep the stored spelling of the name
            request.session["doctor"] = Patient.objects.filter(
                doctor__iexact=name
            ).first().doctor
            return redirect("dashboard")
    return render(request, "doctor/select_doctor.html", {"doctors": doctors})


def logout_doctor(request):
    request.session.pop("doctor", None)
    return redirect("select_doctor")


@doctor_required
def dashboard(request, doctor):
    patients = Patient.objects.filter(doctor__iexact=doctor).annotate(
        urgency=Case(
            When(priority__iexact="emergency", then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    ).order_by("urgency", "token")
    return render(request, "doctor/dashboard.html", {
        "doctor_name": doctor,
        "waiting": [p for p in patients if p.status == Patient.STATUS_WAITING],
        "in_consultation": [p for p in patients if p.status == Patient.STATUS_IN_CONSULTATION],
        "completed": [p for p in patients if p.status == Patient.STATUS_COMPLETED],
    })


@doctor_required
def register_patient(request, doctor):
    if request.method == "POST":
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.token = (Patient.objects.aggregate(maximum_token=Max("token"))[
                "maximum_token"
            ] or 0) + 1
            patient.doctor = doctor
            patient.save()
            messages.success(request, f"Patient registered with token {patient.token}.")
            return redirect("patient_detail", token=patient.token)
    else:
        form = PatientRegistrationForm()
    return render(request, "doctor/register_patient.html", {
        "doctor_name": doctor,
        "form": form,
    })


@doctor_required
def patient_detail(request, doctor, token):
    patient = _own_patient(doctor, token)
    return render(request, "doctor/patient_detail.html", {
        "doctor_name": doctor,
        "patient": patient,
        "prescriptions": patient.current_prescriptions,
    })


@doctor_required
@require_POST
def examine(request, doctor, token):
    patient = _own_patient(doctor, token)
    if patient.status == Patient.STATUS_COMPLETED:
        messages.error(request, "This token is already completed.")
    else:
        findings = request.POST.get("examination", "").strip()
        if not findings:
            messages.error(request, "Examination findings cannot be empty.")
        else:
            patient.examination = findings
            patient.status = Patient.STATUS_IN_CONSULTATION
            patient.save()
            messages.success(request, "Examination saved. Status updated to In Consultation.")
    return redirect("patient_detail", token=token)


@doctor_required
@require_POST
def prescribe(request, doctor, token):
    patient = _own_patient(doctor, token)
    if patient.status == Patient.STATUS_COMPLETED:
        messages.error(request, "This token is already completed.")
    elif not patient.examination.strip():
        messages.error(request, "Record examination findings before providing a prescription.")
    else:
        medicine = request.POST.get("medicine", "").strip()
        dosage = request.POST.get("dosage", "").strip()
        instructions = request.POST.get("instructions", "").strip()
        if not (medicine and dosage and instructions):
            messages.error(request, "All prescription fields are required.")
        else:
            patient.prescriptions.create(
                medicine=medicine, dosage=dosage, instructions=instructions
            )
            messages.success(request, "Prescription saved successfully.")
    return redirect("patient_detail", token=token)


@doctor_required
@require_POST
def complete(request, doctor, token):
    patient = _own_patient(doctor, token)
    if patient.status == Patient.STATUS_COMPLETED:
        messages.error(request, "This token is already completed.")
    elif not patient.examination.strip():
        messages.error(request, "Examine the patient before completing the token.")
    else:
        with transaction.atomic():
            visit = Visit.objects.create(
                patient=patient,
                doctor=doctor,
                problem=patient.problem,
                priority=patient.priority,
                examination=patient.examination,
            )
            patient.current_prescriptions.update(visit=visit)
            patient.status = Patient.STATUS_COMPLETED
            patient.save()
        messages.success(request, "Token marked as completed. Consultation history saved.")
    return redirect("patient_detail", token=token)


@doctor_required
def history(request, doctor, token):
    patient = _own_patient(doctor, token)
    visits = patient.visits.prefetch_related("prescriptions")
    return render(request, "doctor/history.html", {
        "doctor_name": doctor, "patient": patient, "visits": visits,
    })
