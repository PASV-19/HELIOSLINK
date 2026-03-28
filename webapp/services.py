# services.py

from datetime import timedelta
from django.utils.timezone import now
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.db.models import Sum
from django.db.models.functions import TruncDate

from .models import Registro, Sensor, Organizacion, Microcontrolador, Usuario

#Import modules for Reportes
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

# -------------------------
# SENSOR HELPERS
# -------------------------
def get_sensor(sensor_type):
    return Sensor.objects.filter(type_sen=sensor_type).first()


# -------------------------
# PANEL ANGLE
# -------------------------
def get_latest_angle():
    sensor = get_sensor("angle")

    if not sensor:
        return None

    registro = (
        Registro.objects
        .filter(sensor=sensor)
        .order_by('-datetime')
        .first()
    )

    return registro.value if registro else None


# -------------------------
# PRODUCTION RECORDS
# -------------------------
def get_today_production_records():
    sensor = get_sensor("production")

    if not sensor:
        return Registro.objects.none()

    return Registro.objects.filter(
        sensor=sensor,
        datetime__date=now().date()
    ).order_by('datetime')


# -------------------------
# CURRENT EXPOSURE
# -------------------------
def calculate_current_exposure(records, threshold=5):
    exposure = timedelta()

    for r in records:
        if r.value > threshold:
            exposure += timedelta(seconds=15)

    return exposure


# -------------------------
# DAILY EXPOSURE HISTORY
# -------------------------
def get_daily_exposure_history():
    sensor = get_sensor("production")

    if not sensor:
        return []

    records = (
        Registro.objects
        .filter(sensor=sensor)
        .annotate(day=TruncDate('datetime'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    result = []
    for r in records:
        hours = (r['count'] * 15) / 3600
        result.append({
            "day": r['day'],
            "hours": round(hours, 2)
        })

    return result

def get_current_day_energy():
    prod_sensor = get_sensor("production")
    cons_sensor = get_sensor("consumption")

    if not prod_sensor or not cons_sensor:
        return {"labels": [], "production": [], "consumption": []}

    prod_records = Registro.objects.filter(sensor=prod_sensor).order_by('datetime')
    cons_records = Registro.objects.filter(sensor=cons_sensor).order_by('datetime')

    labels = [r.datetime.strftime("%H:%M") for r in prod_records]

    return {
        "labels": labels,
        "production": [r.value for r in prod_records],
        "consumption": [r.value for r in cons_records]
    }
def get_daily_energy():
    prod_sensor = get_sensor("production")
    cons_sensor = get_sensor("consumption")

    prod = (
        Registro.objects
        .filter(sensor=prod_sensor)
        .annotate(day=TruncDate('datetime'))
        .values('day')
        .annotate(total=Sum('value'))
        .order_by('day')
    )

    cons = (
        Registro.objects
        .filter(sensor=cons_sensor)
        .annotate(day=TruncDate('datetime'))
        .values('day')
        .annotate(total=Sum('value'))
        .order_by('day')
    )

    return {
        "labels": [str(p["day"]) for p in prod],
        "production": [p["total"] for p in prod],
        "consumption": [c["total"] for c in cons]
    }
## Reportes logic
def get_user_organization_data(user):
    try:
        usuario = Usuario.objects.get(user=user)
        org = usuario.org
    except Usuario.DoesNotExist:
        return None

    return {
        "organization": {
            "name": org.name_org,
            "location": org.ubica_org,
            "phone": org.tel
        },
        "user": {
            "username": user.username,
            "email": user.email
        }
    }

def get_network_summary(user):
    try:
        usuario = Usuario.objects.get(user=user)
        org = usuario.org

        devices = Microcontrolador.objects.filter(org=org)

    except Usuario.DoesNotExist:
        return {
            "total_devices": 0,
            "devices": []
        }

    device_list = []
    for d in devices:
        device_list.append({
            "name": d.name_mic,
            "ip": d.ip_add,
            "mac": d.mac_add
        })

    return {
        "total_devices": devices.count(),
        "devices": device_list
    }

def get_historical_data_range(start_date, end_date):
    sensor = get_sensor("production")

    if not sensor:
        return []

    records = (
        Registro.objects
        .filter(
            sensor=sensor,
            datetime__date__range=[start_date, end_date]
        )
        .annotate(day=TruncDate('datetime'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    result = []
    for r in records:
        hours = (r['count'] * 15) / 3600
        result.append({
            "day": r['day'],
            "hours": round(hours, 2)
        })

    return result
## Charts for the reports
def generate_history_chart(history_data):
    if not history_data:
        return None

    x = [str(d["day"]) for d in history_data]
    y = [d["hours"] for d in history_data]

    return generate_chart(x, y, "Horas de exposición")

def generate_network_chart(network_data):
    total = network_data["total_devices"]

    return generate_chart(
        ["Devices"],
        [total],
        "Total de dispositivos"
    )

def build_report_context(user, options):
    base = get_user_organization_data(user)

    context = {
        "organization": base["organization"],
        "user": base["user"],
        "generated_at": now(),
    }

    # =========================
    # NETWORK
    # =========================
    if options.get("include_network"):
        network = get_network_summary(user)
        context["network"] = network

        if options.get("presentation") == "charts":
            context["network_chart"] = generate_network_chart(network)

    # =========================
    # HISTORY
    # =========================
    if options.get("include_history"):
        history = get_historical_data_range(
            options.get("start_date"),
            options.get("end_date")
        )

        context["history"] = history

        if options.get("presentation") == "charts":
            context["history_chart"] = generate_history_chart(history)

    # FLAGS
    context["include_network"] = options.get("include_network")
    context["include_history"] = options.get("include_history")
    context["presentation"] = options.get("presentation")

    return context
