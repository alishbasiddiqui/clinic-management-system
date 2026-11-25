
from django.urls import path
from . import views

app_name = "patients"

urlpatterns = [
    path("", views.patient_list, name="patient_list"),
    path(
        "register/",
        views.register_patient,
        name="register_patient",
    ),
    path(
        "patients/<int:pk>/",
        views.patient_detail,
        name="patient_detail",
    ),
    path("payments/", views.payment_list, name="payment_list"),
    path(
        "assignments/",
        views.assignment_list,
        name="assignment_list",
    ),
]