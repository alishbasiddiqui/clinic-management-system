import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.PositiveIntegerField(unique=True)),
                ("patient_id", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("age", models.PositiveIntegerField()),
                ("gender", models.CharField(max_length=20)),
                ("problem", models.CharField(max_length=255)),
                ("priority", models.CharField(choices=[("Normal", "Normal"), ("Emergency", "Emergency")], default="Normal", max_length=20)),
                ("doctor", models.CharField(max_length=100)),
                ("status", models.CharField(choices=[("Waiting", "Waiting"), ("In Consultation", "In Consultation"), ("Completed", "Completed")], default="Waiting", max_length=20)),
                ("examination", models.TextField(blank=True)),
            ],
            options={"ordering": ["token"]},
        ),
        migrations.CreateModel(
            name="Visit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_time", models.DateTimeField(auto_now_add=True)),
                ("doctor", models.CharField(max_length=100)),
                ("problem", models.CharField(max_length=255)),
                ("priority", models.CharField(max_length=20)),
                ("examination", models.TextField()),
                ("status", models.CharField(default="Completed", max_length=20)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="visits", to="doctor.patient")),
            ],
            options={"ordering": ["date_time"]},
        ),
        migrations.CreateModel(
            name="Prescription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("medicine", models.CharField(max_length=150)),
                ("dosage", models.CharField(max_length=150)),
                ("instructions", models.CharField(max_length=255)),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prescriptions", to="doctor.patient")),
                ("visit", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="prescriptions", to="doctor.visit")),
            ],
        ),
    ]
