# Clinic Management System (Django)

Doctor dashboard: select a doctor, register patients, manage waiting tokens, examine patients, write prescriptions, complete consultations, and review saved visit history. Emergency patients are listed first.

## Run
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed_patients
    python manage.py runserver
Open http://127.0.0.1:8000/

After selecting a doctor, use **Register patient** to add records assigned to that doctor. The application stores patient and consultation data in `db.sqlite3`; `clinic_data.json` is only used by the separate legacy console module.

Optional: `python manage.py createsuperuser` for /admin/. Run tests: `python manage.py test`.

## Production
Set env vars `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS=yourdomain.com`.
Note: doctors are selected by name with no password; add real authentication before using with real patient data.
