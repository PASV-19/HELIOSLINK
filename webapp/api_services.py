import time
import requests
from django.conf import settings
from .models import Registro, Microcontrolador, Sensor, Organizacion


# =========================
# TOKEN VALIDATION
# =========================
def is_authorized(request):
    token = request.headers.get("Authorization")
    return token == f"Token {settings.API_TOKEN}"


# =========================
# STORE REGISTROS
# =========================
def store_energy(production, consumption):
    sensor = Sensor.objects.get(pk=1)  # corriente

    Registro.objects.create(
        value=production,
        type_regis="production",
        sensor=sensor
    )

    Registro.objects.create(
        value=consumption,
        type_regis="consumption",
        sensor=sensor
    )


def store_angle(angle):
    sensor = Sensor.objects.get(pk=3)  # movimiento

    Registro.objects.create(
        value=angle,
        type_regis="angle",
        sensor=sensor
    )


def store_battery(percentage):
    sensor = Sensor.objects.get(pk=2)  # bateria

    Registro.objects.create(
        value=percentage,
        type_regis="percentage",
        sensor=sensor
    )


# =========================
# DEVICES (SNAPSHOT OVERWRITE)
# =========================
def overwrite_devices(devices):
    org = Organizacion.objects.get(pk=1)

    # Delete all previous records
    Microcontrolador.objects.all().delete()

    new_objects = []
    for i, device in enumerate(devices, start=1):
        new_objects.append(
            Microcontrolador(
                name_mic=f"Dispositivo {i}",
                ip_add=device["ip"],
                mac_add=device["mac"],
                org=org
            )
        )

    Microcontrolador.objects.bulk_create(new_objects)


# =========================
# ESP COMMUNICATION (GET BATTERY)
# =========================
def fetch_battery_from_esp():
    url = f"http://{settings.ESP_IP}/battery"

    for _ in range(settings.ESP_RETRIES):
        try:
            response = requests.get(url, timeout=settings.ESP_TIMEOUT)

            if response.status_code == 200:
                data = response.json()
                return data.get("battery")

        except requests.RequestException:
            time.sleep(2)  # short delay before retry

    return None
