from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# =========================
# ORGANIZACION
# =========================
class Organizacion(models.Model):
    name_org = models.CharField(max_length=100)
    ubica_org = models.CharField(max_length=150)
    tel = models.IntegerField()

    def __str__(self):
        return self.name_org


# =========================
# USUARIO (EXTENSION)
# =========================
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status_usr = models.BooleanField(default=True)
    org = models.ForeignKey(Organizacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


# =========================
# MICROCONTROLADORES
# =========================
class Microcontrolador(models.Model):
    name_mic = models.CharField(max_length=100)
    ip_add = models.GenericIPAddressField()
    mac_add = models.CharField(max_length=17, unique=True)
    org = models.ForeignKey(Organizacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_mic


# =========================
# SENSORES
# =========================
class Sensor(models.Model):
    name_sen = models.CharField(max_length=100)
    type_sen = models.CharField(max_length=100)
    status_sen = models.BooleanField(default=True)
    org = models.ForeignKey(Organizacion, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_sen


# =========================
# REGISTROS
# =========================
class Registro(models.Model):
    value = models.FloatField()
    type_regis = models.CharField(max_length=100)
    anomalia = models.BooleanField(default=False)
    datetime = models.DateTimeField(default=now)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.type_regis} - {self.value}"
