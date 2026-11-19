from django.db import models


class Patient(models.Model):
    PRIORITY_CHOICES = [("Normal", "Normal"), ("Emergency", "Emergency")]
    STATUS_WAITING = "Waiting"
    STATUS_IN_CONSULTATION = "In Consultation"
    STATUS_COMPLETED = "Completed"
    STATUS_CHOICES = [
        (STATUS_WAITING, "Waiting"),
        (STATUS_IN_CONSULTATION, "In Consultation"),
        (STATUS_COMPLETED, "Completed"),
    ]

    token = models.PositiveIntegerField(unique=True)
    patient_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20)
    problem = models.CharField(max_length=255)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="Normal")
    doctor = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_WAITING)
    examination = models.TextField(blank=True)

    class Meta:
        ordering = ["token"]

    def __str__(self):
        return f"{self.token} - {self.name}"

    @property
    def is_emergency(self):
        return self.priority.lower() == "emergency"

    @property
    def current_prescriptions(self):
        """Prescriptions not yet attached to a completed visit."""
        return self.prescriptions.filter(visit__isnull=True)


class Visit(models.Model):
    """Snapshot saved when a token is completed."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    date_time = models.DateTimeField(auto_now_add=True)
    doctor = models.CharField(max_length=100)
    problem = models.CharField(max_length=255)
    priority = models.CharField(max_length=20)
    examination = models.TextField()
    status = models.CharField(max_length=20, default="Completed")

    class Meta:
        ordering = ["date_time"]

    def __str__(self):
        return f"{self.patient.name} - {self.date_time:%Y-%m-%d %H:%M}"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescriptions")
    visit = models.ForeignKey(
        Visit, on_delete=models.SET_NULL, null=True, blank=True, related_name="prescriptions"
    )
    medicine = models.CharField(max_length=150)
    dosage = models.CharField(max_length=150)
    instructions = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.medicine} ({self.dosage})"
