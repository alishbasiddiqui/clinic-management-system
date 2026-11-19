
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Patient, Payment, DoctorAssignment
from .forms import PatientRegistrationForm


def register_patient(request):
    today = timezone.localdate()

    # Check today's registered patients
    daily_patient_count = Patient.objects.filter(
        registered_at__date=today
    ).count()

    if request.method == "POST":

        # Stop registration if daily limit is reached
        if daily_patient_count >= 50:
            messages.error(
                request,
                "Daily registration limit reached. Maximum 50 patients are allowed per day."
            )
            form = PatientRegistrationForm(request.POST)

        else:
            form = PatientRegistrationForm(request.POST)

            if form.is_valid():
                with transaction.atomic():

                    # Recheck limit before saving
                    current_count = Patient.objects.filter(
                        registered_at__date=today
                    ).count()

                    if current_count >= 50:
                        messages.error(
                            request,
                            "Daily registration limit reached. Maximum 50 patients are allowed per day."
                        )
                    else:
                        patient = form.save()

                        Payment.objects.create(
                            patient=patient,
                            amount=form.cleaned_data["payment_amount"],
                            payment_method=form.cleaned_data["payment_method"],
                            payment_status=form.cleaned_data["payment_status"],
                        )

                        DoctorAssignment.objects.create(
                            patient=patient,
                            doctor_type=form.cleaned_data["doctor_type"],
                        )

                        messages.success(
                            request,
                            "Patient registered successfully."
                        )

                        return redirect(
                            "patients:patient_detail",
                            pk=patient.pk
                        )

    else:
        form = PatientRegistrationForm()

    return render(
        request,
        "patients/register_patient.html",
        {
            "form": form,
            "daily_patient_count": daily_patient_count,
            "daily_limit": 50,
        }
    )


def patient_list(request):
    patients = (
        Patient.objects
        .select_related("doctor_assignment")
        .prefetch_related("payments")
        .order_by("-registered_at")
    )

    return render(
        request,
        "patients/patient_list.html",
        {"patients": patients}
    )


def patient_detail(request, pk):
    patient = get_object_or_404(
        Patient.objects
        .select_related("doctor_assignment")
        .prefetch_related("payments"),
        pk=pk
    )

    return render(
        request,
        "patients/patient_detail.html",
        {"patient": patient}
    )


def payment_list(request):
    payments = Payment.objects.select_related(
        "patient"
    ).order_by("-payment_date")

    return render(
        request,
        "patients/payment_list.html",
        {"payments": payments}
    )


def assignment_list(request):
    assignments = DoctorAssignment.objects.select_related(
        "patient"
    ).order_by("-assigned_at")

    return render(
        request,
        "patients/assignment_list.html",
        {"assignments": assignments}
    )
