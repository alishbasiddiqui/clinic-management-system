from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.select_doctor, name="select_doctor"),
    path("logout/", views.logout_doctor, name="logout_doctor"),
    path("patients/register/", views.register_patient, name="register_patient"),
    path("patient/<int:token>/", views.patient_detail, name="patient_detail"),
    path("patient/<int:token>/examine/", views.examine, name="examine"),
    path("patient/<int:token>/prescribe/", views.prescribe, name="prescribe"),
    path("patient/<int:token>/complete/", views.complete, name="complete"),
    path("patient/<int:token>/history/", views.history, name="history"),
]
