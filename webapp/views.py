# Import the necessary modules
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib import messages

from .models import Organizacion, Usuario #Import ORM for registration
from .services import (
    get_latest_angle,
    get_today_production_records,
    calculate_current_exposure,
    get_daily_exposure_history
)

# Create your views here.

## Login related: user login, account creation, password reset
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("graf_info")
        else:
            return render(request, "login.html", {
                "error": "Usuario o contraseña incorrectos"
            })
    return render(request, "login.html")

def crear_cuenta(request):
    if request.method == "POST":
		# === Capturar datos del formulario ===
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        name_org = request.POST.get("name_org")
        ubica_org = request.POST.get("ubica_org")
        tel = request.POST.get("tel")

        # === Validaciones básicas ===
        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe.")
            return redirect("crear_cuenta")

        if User.objects.filter(email=email).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect("crear_cuenta")

        try:
            with transaction.atomic():
			    # === Crear organización ===
                org = Organizacion.objects.create(
				    name_org=name_org,
				    ubica_org=ubica_org,
				    tel=tel
			    )

			    # === Crear usuario (IMPORTANTE: usar create_user) ===
                user = User.objects.create_user(
			    	username=username,
			    	email=email,
			    	password=password
			    )
				# === Crear perfil extendido ===
                Usuario.objects.create(
					user=user,
					org=org
				)

            messages.success(request, "Cuenta creada correctamente.")
            return redirect("login")

        except Exception as e:
            messages.error(request, f"Error al crear la cuenta: {str(e)}")
            return redirect("crear_cuenta")

    return render(request, "crear_cuenta.html")

def restablecer(request):
    return render(request, "restablecer.html")

## Real time related / ESP32 redirection
def dashboard(request):
    return render(request, "dashboard.html")

## Non real-time related / informative pages
def graf_info_view(request):
    angle = get_latest_angle()

    today_records = get_today_production_records()

    current_exposure = calculate_current_exposure(today_records)

    history = get_daily_exposure_history()

    context = {
        "angle": angle,
        "current_exposure": current_exposure,
        "history": history,
        "status": "charging" if angle else "idle"
    }

    return render(request, "graf_info.html", context)

def graf_hist(request):
    return render(request, "graf_hist.html")

def reportes(request):
    return render(request, "reportes.html")

def user_info(request):
    return render(request, "user_info.html")

def net_info(request):
    return render(request, "net_info.html")
