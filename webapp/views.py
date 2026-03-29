# Import the necessary modules
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.contrib import messages

from .models import Organizacion, Usuario, Microcontrolador, Usuario #Import ORM for registration
from .services import (
    #Import for graf_info
    get_latest_angle,
    get_today_production_records,
    calculate_current_exposure,
    get_daily_exposure_history,
    #Import for graf_hist
    get_current_day_energy,
    get_daily_energy,
    #Import for reportes
    build_report_context,
)
##Imports for Reportes
from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime
from weasyprint import HTML

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
        "status": "charging" if angle is not None else "idle"
    }

    return render(request, "graf_info.html", context)

def graf_hist_view(request):
    current_day = get_current_day_energy()
    daily = get_daily_energy()
    exposure = get_daily_exposure_history()

    context = {
        "current_day": current_day,
        "daily": daily,
        "exposure": exposure
    }
    return render(request, "graf_hist.html", context)

def reportes_view(request):
    return render(request, "reportes.html")

def generar_pdf(request):
    if request.method != "POST":
        return redirect("reportes")

    # =========================
    # OPTIONS FROM FORM
    # =========================
    include_network = "include_network" in request.POST
    include_history = "include_history" in request.POST
    presentation = request.POST.get("presentation", "tables")

    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    # =========================
    # VALIDATION
    # =========================
    if include_history:
        if not start_date or not end_date:
            return HttpResponse("Error: Debes seleccionar fechas", status=400)

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if (end_date - start_date).days > 14:
            return HttpResponse("Error: Máximo 2 semanas de rango", status=400)

    else:
        start_date = None
        end_date = None

    # =========================
    # BUILD CONTEXT
    # =========================
    options = {
        "include_network": include_network,
        "include_history": include_history,
        "presentation": presentation,
        "start_date": start_date,
        "end_date": end_date
    }

    context = build_report_context(request.user, options)

    # =========================
    # RENDER PDF
    # =========================
    html_string = render_to_string("reportes_pdf.html", context)

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reporte.pdf"'

    return response

def user_info_view(request):
    user = request.user

    try:
        usuario = Usuario.objects.get(user=user)
    except Usuario.DoesNotExist:
        return render(request, "user_info.html", {
            "error": "Usuario no encontrado"
        })

    org = usuario.org

    context = {
        "user": user,
        "usuario": usuario,
        "org": org
    }

    # POST: Update user data
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            if email:
                user.email = email

            if password:
                user.password = make_password(password)

            user.save()

            context["success"] = "Datos actualizados correctamente"

        except Exception as e:
            context["error"] = str(e)
    return render(request, "user_info.html", context)

def net_info_view(request):
    try:
        usuario = Usuario.objects.get(user=request.user)
        org = usuario.org

        devices = Microcontrolador.objects.filter(org=org)

    except Usuario.DoesNotExist:
        devices = []

    context = {
        "devices": devices
    }
    return render(request, "net_info.html", context)
