
from django.db import models
from patients.models import Patient


class QueueToken(models.Model):
    STATUS_CHOICES = [
        ("Waiting", "Waiting"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name="queue_token"
    )
    token_number = models.PositiveIntegerField()
    token_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Waiting"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["token_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["token_date", "token_number"],
                name="unique_daily_queue_token"
            )
        ]

    def __str__(self):
        return f"T{self.token_number:03d} - {self.patient.name}"
