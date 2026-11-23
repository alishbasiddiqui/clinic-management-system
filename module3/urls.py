from django.urls import path
from . import views

urlpatterns = [
    path('', views.token_dashboard, name='token_dashboard'),
]