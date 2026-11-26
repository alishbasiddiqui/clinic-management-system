"""
URL configuration for the Clinic Management System.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication and role-specific dashboards own the site root.
    path("", include("clinic.urls")),
    # Keep each feature module under its own URL prefix to avoid root collisions.
    path("patients/", include("patients.urls")),
    path("doctor/", include("doctor.urls")),
]
