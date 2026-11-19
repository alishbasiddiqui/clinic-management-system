from django.test import TestCase
from django.urls import reverse

from .models import Patient, Payment, DoctorAssignment


class PatientRegistrationTests(TestCase):

    def test_registration_page_opens(self):
        response = self.client.get(
            reverse("patients:register_patient")
        )

        self.assertEqual(response.status_code, 200)

    def test_patient_registration_saves_all_records(self):
        response = self.client.post(
            reverse("patients:register_patient"),
            {
                "name": "Test Patient",
                "gender": "male",
                "age": 25,
                "is_emergency": "on",
                "payment_amount": "500.00",
                "payment_method": "cash",
                "payment_status": "paid",
                "doctor_type": "main_doctor",
            },
        )

        self.assertEqual(response.status_code, 302)

        patient = Patient.objects.get(name="Test Patient")

        self.assertTrue(patient.token)
        self.assertTrue(patient.is_emergency)
        self.assertTrue(patient.patient_code.startswith("PAT-"))

        self.assertEqual(
            Payment.objects.filter(patient=patient).count(),
            1,
        )

        assignment = DoctorAssignment.objects.get(patient=patient)

        self.assertEqual(
            assignment.doctor_type,
            "main_doctor",
        )