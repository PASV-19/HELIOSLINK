# Import the necessary modules
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib import messages

from .models import Organizacion, Usuario #Import ORM for registration

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

    return render(request, "crear-cuenta.html")

def graf_info(request):
    return render(request, "graf_info.html")

def reportes(request):
    return render(request, "reportes.html")

def user_info(request):
    return render(request, "user_info.html")

def informacion_red(request):
    return render(request, "informacion-red.html")

def restablecer(request):
    return render(request, "restablecer.html")
