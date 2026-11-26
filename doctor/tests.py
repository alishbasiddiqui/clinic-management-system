import importlib.util
import io
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings

from .models import Patient, Prescription, Visit


def load_consultation_module():
    module_path = Path(__file__).resolve().parents[1] / "doctor_module.py"
    spec = importlib.util.spec_from_file_location("consultation_prescription_module", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ConsultationPrescriptionModuleTests(SimpleTestCase):
    def test_get_doctor_patients_is_case_insensitive(self):
        module = load_consultation_module()
        patients = [
            {"token": 101, "name": "Ali Khan", "doctor": "Dr. Ahmed", "status": "Waiting"},
            {"token": 102, "name": "Sara Malik", "doctor": "dr. usman", "status": "Waiting"},
            {"token": 103, "name": "Usman Ali", "doctor": "DR. AHMED", "status": "Waiting"},
        ]

        assigned = module.get_doctor_patients(patients, "dr. ahmed")

        self.assertEqual([patient["token"] for patient in assigned], [101, 103])

    def test_find_patient_returns_matching_token_for_assigned_doctor(self):
        module = load_consultation_module()
        patients = [
            {"token": 101, "name": "Ali Khan", "doctor": "Dr. Ahmed", "status": "Waiting"},
            {"token": 202, "name": "Sara Malik", "doctor": "Dr. Usman", "status": "Waiting"},
        ]

        with patch("builtins.input", return_value="101"):
            patient = module.find_patient(patients, "Dr. Ahmed")

        self.assertIsNotNone(patient)
        self.assertEqual(patient["name"], "Ali Khan")

    def test_view_waiting_patients_prioritizes_emergency_cases(self):
        module = load_consultation_module()
        patients = [
            {"token": 101, "name": "Ali Khan", "problem": "Fever", "priority": "Normal", "doctor": "Dr. Ahmed", "status": "Waiting"},
            {"token": 202, "name": "Sara Malik", "problem": "Difficulty breathing", "priority": "Emergency", "doctor": "Dr. Ahmed", "status": "Waiting"},
            {"token": 303, "name": "Usman Ali", "problem": "Back pain", "priority": "Normal", "doctor": "Dr. Usman", "status": "Waiting"},
        ]

        output = io.StringIO()
        with redirect_stdout(output):
            module.view_waiting_patients(patients, "Dr. Ahmed")

        text = output.getvalue()
        self.assertIn("Sara Malik", text)
        self.assertIn("Ali Khan", text)
        self.assertLess(text.index("Sara Malik"), text.index("Ali Khan"))

    def test_examine_patient_records_findings_and_updates_status(self):
        module = load_consultation_module()
        patient = {
            "token": 11,
            "name": "Ali Khan",
            "doctor": "Dr. Ahmed",
            "status": "Waiting",
            "examination": "",
            "priority": "Normal",
        }

        with patch.object(module, "save_patients", return_value=True), \
             patch("builtins.input", side_effect=["11", "High fever and mild dehydration"]):
            output = io.StringIO()
            with redirect_stdout(output):
                module.examine_patient([patient], "Dr. Ahmed")

        self.assertEqual(patient["status"], "In Consultation")
        self.assertEqual(patient["examination"], "High fever and mild dehydration")
        self.assertIn("Examination findings saved.", output.getvalue())

    def test_load_patients_creates_sample_data_when_file_missing(self):
        module = load_consultation_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_file = Path(temp_dir) / "missing_clinic_data.json"
            module.DATA_FILE = missing_file

            patients = module.load_patients()

        self.assertIsInstance(patients, list)
        self.assertGreater(len(patients), 0)
        self.assertEqual(patients[0]["doctor"], "Dr. Ahmed")


@override_settings(ROOT_URLCONF="doctor.urls")
class ClinicWorkflowTests(TestCase):
    def setUp(self):
        Patient.objects.create(
            token=101,
            patient_id="P101",
            name="Alex Patient",
            age=36,
            gender="Other",
            problem="Headache",
            priority="Normal",
            doctor="Dr. Ahmed",
        )
        session = self.client.session
        session["doctor"] = "Dr. Ahmed"
        session.save()

    def test_doctor_selection_logs_in_case_insensitively(self):
        self.client.session.flush()
        self.assertContains(self.client.get("/login/"), "Dr. Ahmed")
        response = self.client.post("/login/", {"doctor": "dr. ahmed"})
        self.assertRedirects(response, "/")
        self.assertEqual(self.client.session["doctor"], "Dr. Ahmed")
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_registration_consultation_prescription_and_history(self):
        registration = self.client.post(
            "/patients/register/",
            {
                "patient_id": "P102",
                "name": "Sam Patient",
                "age": 29,
                "gender": "Female",
                "problem": "Breathing difficulty",
                "priority": "Emergency",
            },
        )
        self.assertRedirects(registration, "/patient/102/")
        patient = Patient.objects.get(token=102)
        self.assertEqual(patient.doctor, "Dr. Ahmed")
        self.assertEqual(patient.status, Patient.STATUS_WAITING)

        dashboard = self.client.get("/")
        self.assertContains(dashboard, "Sam Patient")
        self.assertLess(
            dashboard.content.index(b"Sam Patient"),
            dashboard.content.index(b"Alex Patient"),
        )

        examine_response = self.client.post(
            "/patient/102/examine/",
            {"examination": "Patient assessed and stable."},
        )
        self.assertRedirects(examine_response, "/patient/102/")
        patient.refresh_from_db()
        self.assertEqual(patient.status, Patient.STATUS_IN_CONSULTATION)

        prescription_response = self.client.post(
            "/patient/102/prescribe/",
            {
                "medicine": "Example medicine",
                "dosage": "One tablet",
                "instructions": "Take after a meal",
            },
        )
        self.assertRedirects(prescription_response, "/patient/102/")
        self.assertEqual(Prescription.objects.filter(patient=patient).count(), 1)

        complete_response = self.client.post("/patient/102/complete/")
        self.assertRedirects(complete_response, "/patient/102/")
        patient.refresh_from_db()
        visit = Visit.objects.get(patient=patient)
        self.assertEqual(patient.status, Patient.STATUS_COMPLETED)
        self.assertEqual(visit.prescriptions.count(), 1)
        self.assertContains(self.client.get("/patient/102/history/"), "Example medicine")

    def test_doctor_routes_require_a_selected_doctor(self):
        self.client.session.flush()
        response = self.client.get("/patients/register/")
        self.assertRedirects(response, "/login/")

    def test_register_form_rejects_duplicate_patient_id(self):
        response = self.client.post(
            "/patients/register/",
            {
                "patient_id": "P101",
                "name": "Duplicate ID",
                "age": 20,
                "gender": "Other",
                "problem": "Checkup",
                "priority": "Normal",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Patient with this Patient id already exists.")
        self.assertEqual(Patient.objects.count(), 1)
