from django.core.management.base import BaseCommand
from doctor.models import Patient

SAMPLES = [
    (101, "P001", "Ali Khan", 25, "Male", "Fever and headache", "Normal", "Dr. Ahmed"),
    (102, "P002", "Sara Malik", 32, "Female", "Difficulty breathing", "Emergency", "Dr. Ahmed"),
    (103, "P003", "Usman Ali", 40, "Male", "Stomach pain", "Normal", "Dr. Ahmed"),
    (104, "P004", "Ayesha Noor", 28, "Female", "Cough", "Normal", "Dr. Usman"),
]


class Command(BaseCommand):
    help = "Create the sample patients from the original console module."

    def handle(self, *args, **options):
        created = 0
        for token, pid, name, age, gender, problem, priority, doctor in SAMPLES:
            _, was_new = Patient.objects.get_or_create(
                token=token,
                defaults=dict(patient_id=pid, name=name, age=age, gender=gender,
                              problem=problem, priority=priority, doctor=doctor),
            )
            created += was_new
        self.stdout.write(self.style.SUCCESS(f"{created} sample patient(s) created."))
