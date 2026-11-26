# Clinic Management System

A Django-based clinic workflow project for receptionist and doctor roles.

## Current project modules

- Receptionist login and dashboard
- Patient registration, payments, and doctor assignment
- Doctor consultation, examination notes, prescriptions, and visit history
- Emergency-first ordering in the doctor consultation module

## Requirements

- Python 3.14
- Django 6.1.2
- SQLite (development database)

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ and use the login page.

## Run tests

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Notes

- The application is under active development and is not production-ready.
- Configure a unique `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS` before deployment.
- Do not commit local databases, environment files, or Python cache files.
