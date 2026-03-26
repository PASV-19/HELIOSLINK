# services.py

from datetime import timedelta
from django.utils.timezone import now
from django.db.models.functions import TruncDate
from django.db.models import Count

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
