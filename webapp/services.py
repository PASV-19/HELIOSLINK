# services.py

from datetime import timedelta
from django.utils.timezone import now
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.db.models import Sum
from django.db.models.functions import TruncDate

from .models import Registro, Sensor


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
