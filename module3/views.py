
from django.shortcuts import render
from django.utils import timezone

patients = []
next_token = 1
token_date = timezone.localdate()


def token_dashboard(request):
    global next_token, token_date, patients

    today = timezone.localdate()
    message = ""

    if today != token_date:
        patients = []
        next_token = 1
        token_date = today

    if request.method == "POST":
        name = request.POST.get("patient_name", "").strip()
        is_emergency = request.POST.get("is_emergency") == "on"

        if not name:
            message = "Please enter a valid patient name."

        elif len(patients) >= 50:
            message = "Daily limit of 50 tokens has been reached."

        else:
            token = f"T{next_token:03d}"

            patient = {
                "name": name,
                "token": token,
                "emergency": is_emergency,
            }

            if is_emergency:
                patients.insert(0, patient)
                message = f"EMERGENCY! {name} received token {token}."
            else:
                patients.append(patient)
                message = f"{name} received token {token}."

            next_token += 1

    return render(
        request,
        "module3/page.html",
        {"patients": patients, "message": message},
    )
