from django.apps import apps
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import ClinicProfile

RECEPTIONIST = ClinicProfile.RECEPTIONIST
DOCTOR = ClinicProfile.DOCTOR
ALLOWED_ROLES = {RECEPTIONIST, DOCTOR}


def get_user_role(user):
    if not getattr(user, 'is_authenticated', False):
        return None

    try:
        role = user.clinic_profile.role
    except ClinicProfile.DoesNotExist:
        return None

    if role in ALLOWED_ROLES:
        return role
    return None


def _allowed_dashboard_redirect(user, redirect_to):
    role = get_user_role(user)
    if not redirect_to:
        return False

    if role == RECEPTIONIST and redirect_to.startswith(reverse('receptionist_dashboard')):
        return True
    if role == DOCTOR and redirect_to.startswith(reverse('doctor_dashboard')):
        return True
    return False


def _safe_get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def _date_field_for(model):
    candidate_names = ('created_at', 'created_on', 'registered_at', 'registration_date', 'date_registered', 'created')
    if model is None:
        return None
    field_names = {field.name for field in model._meta.get_fields() if hasattr(field, 'name')}
    for candidate in candidate_names:
        if candidate in field_names:
            return candidate
    return None


def _status_field_for(model):
    candidate_names = ('status', 'queue_status', 'state', 'token_status')
    if model is None:
        return None
    field_names = {field.name for field in model._meta.get_fields() if hasattr(field, 'name')}
    for candidate in candidate_names:
        if candidate in field_names:
            return candidate
    return None


def _emergency_field_for(model):
    candidate_names = ('is_emergency', 'emergency', 'priority', 'urgent')
    if model is None:
        return None
    field_names = {field.name for field in model._meta.get_fields() if hasattr(field, 'name')}
    for candidate in candidate_names:
        if candidate in field_names:
            return candidate
    return None


def _is_waiting_status(value):
    if value is None:
        return False
    return str(value).strip().lower() in {'waiting', 'queued', 'in_queue', 'pending'}


def get_receptionist_summary():
    total_patients_today = 0
    waiting_patients = 0
    emergency_waiting = 0

    patient_model = _safe_get_model('clinic', 'Patient')
    queue_model = _safe_get_model('clinic', 'Queue') or _safe_get_model('clinic', 'PatientQueue')

    if patient_model is not None:
        date_field = _date_field_for(patient_model)
        if date_field:
            total_patients_today = patient_model.objects.filter(**{f'{date_field}__date': timezone.localdate()}).count()

    if queue_model is not None:
        status_field = _status_field_for(queue_model)
        emergency_field = _emergency_field_for(queue_model)

        if status_field:
            status_values = [
                str(value).strip().lower()
                for value in queue_model.objects.values_list(status_field, flat=True)
                if value is not None
            ]
            waiting_patients = sum(1 for value in status_values if _is_waiting_status(value))

        if emergency_field:
            emergency_values = [
                value for value in queue_model.objects.values_list(emergency_field, flat=True)
                if value in (True, 'true', 'yes', 'urgent', 'emergency')
            ]
            if status_field:
                emergency_waiting = sum(
                    1
                    for item in queue_model.objects.filter(**{emergency_field: True}).values_list(status_field, flat=True)
                    if _is_waiting_status(item)
                )
            else:
                emergency_waiting = len(emergency_values)

    return {
        'patients_registered_today': total_patients_today,
        'waiting_patients': waiting_patients,
        'emergency_waiting': emergency_waiting,
        'data_available': patient_model is not None or queue_model is not None,
    }


def get_receptionist_queue():
    queue_model = _safe_get_model('clinic', 'Queue') or _safe_get_model('clinic', 'PatientQueue')
    if queue_model is None:
        return {'items': [], 'available': False}

    status_field = _status_field_for(queue_model)
    queryset = queue_model.objects.all()
    if status_field is not None:
        queryset = queryset.order_by(status_field)
    return {'items': list(queryset[:20]), 'available': True}


def get_doctor_queue(user):
    queue_model = _safe_get_model('clinic', 'Queue') or _safe_get_model('clinic', 'PatientQueue')
    if queue_model is None:
        return {'items': [], 'available': False}

    doctor_field = next(
        (name for name in ('doctor', 'assigned_doctor', 'doctor_id', 'assigned_to') if hasattr(queue_model, name)),
        None,
    )
    if doctor_field is None:
        return {'items': [], 'available': True}

    queryset = queue_model.objects.filter(**{doctor_field: user})
    status_field = _status_field_for(queue_model)
    if status_field:
        queryset = queryset.order_by(status_field)
    return {'items': list(queryset[:20]), 'available': True}


def redirect_to_login_if_needed(request):
    if request.user.is_authenticated:
        role = get_user_role(request.user)
        if role is None:
            logout(request)
            request.session.flush()
            messages.error(request, 'Your account does not have an approved clinic role.')
            return redirect('login')
        return redirect('receptionist_dashboard' if role == RECEPTIONIST else 'doctor_dashboard')
    return None


def login_view(request):
    redirect_target = request.POST.get('next') or request.GET.get('next', '')
    if redirect_target and not url_has_allowed_host_and_scheme(redirect_target, allowed_hosts={request.get_host()}):
        redirect_target = ''

    if request.user.is_authenticated:
        return redirect_to_login_if_needed(request)

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html', {'username': username})

        role = get_user_role(user)
        if role is None:
            messages.error(request, 'Your account does not have an approved clinic role.')
            return render(request, 'login.html', {'username': username})

        login(request, user)

        if redirect_target and _allowed_dashboard_redirect(user, redirect_target):
            return redirect(redirect_target)
        return redirect('receptionist_dashboard' if role == RECEPTIONIST else 'doctor_dashboard')

    return render(request, 'login.html')


@login_required(login_url='login')
def receptionist_dashboard(request):
    role = get_user_role(request.user)
    if role != RECEPTIONIST:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')

    summary = get_receptionist_summary()
    queue = get_receptionist_queue()
    context = {
        'user': request.user,
        'summary': summary,
        'queue': queue,
    }
    return render(request, 'receptionist_dashboard.html', context)


@login_required(login_url='login')
def doctor_dashboard(request):
    role = get_user_role(request.user)
    if role != DOCTOR:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')

    queue = get_doctor_queue(request.user)
    context = {
        'user': request.user,
        'queue': queue,
        'next_patient': None,
    }
    return render(request, 'doctor_dashboard.html', context)


@require_POST
@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')
