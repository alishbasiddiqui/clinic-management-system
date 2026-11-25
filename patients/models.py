import uuid
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Patient(models.Model):

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=150)

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    age = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(120),
        ]
    )

    is_emergency = models.BooleanField(default=False)

    # Automatically generated unique token
    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    @property
    def patient_code(self):
        if self.pk:
            return f"PAT-{self.pk:06d}"
        return "PAT-PENDING"

    def __str__(self):
        return f"{self.patient_code} - {self.name}"


class Payment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("bank_transfer", "Bank Transfer"),
        ("mobile_wallet", "Mobile Wallet"),
        ("other", "Other"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("partial", "Partially Paid"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.patient_code} - {self.amount}"


class DoctorAssignment(models.Model):

    DOCTOR_CHOICES = [
        ("main_doctor", "Main Doctor"),
        ("substitute_doctor", "Substitute Doctor"),
    ]

    patient = models.OneToOneField(
        Patient,
        on_delete=models.PROTECT,
        related_name="doctor_assignment"
    )

    doctor_type = models.CharField(
        max_length=30,
        choices=DOCTOR_CHOICES
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.patient.patient_code} - "
            f"{self.get_doctor_type_display()}"
        )