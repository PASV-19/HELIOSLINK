import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .api_services import (
    is_authorized,
    store_energy,
    store_angle,
    overwrite_devices,
    fetch_battery_from_esp,
    store_battery
)

# POST Telemetry data (energy production and consumption)
@csrf_exempt
def api_telemetry_post(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    if not is_authorized(request):
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # DEVICES
    if "devices" in data:
        overwrite_devices(data["devices"])

    # ENERGY
    if "energy_production" in data and "energy_consumption" in data:
        store_energy(
            data["energy_production"],
            data["energy_consumption"]
        )

    # ANGLE
    if "angle" in data:
        store_angle(data["angle"])

    return JsonResponse({"status": "success"})

# GET Battery charge percentage
def api_battery_get(request):
    if request.method != "GET":
        return JsonResponse({"error": "Invalid method"}, status=405)

    battery = fetch_battery_from_esp()

    if battery is None:
        return JsonResponse(
            {"error": "ESP unreachable"},
            status=503
        )

    store_battery(battery)

    return JsonResponse({
        "status": "success",
        "battery": battery
    })
