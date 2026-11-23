from django.contrib.auth.models import User
from django.db import models


class ClinicProfile(models.Model):
    RECEPTIONIST = 'RECEPTIONIST'
    DOCTOR = 'DOCTOR'

    ROLE_CHOICES = [
        (RECEPTIONIST, 'Receptionist'),
        (DOCTOR, 'Doctor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='clinic_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = 'clinic profile'
        verbose_name_plural = 'clinic profiles'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
