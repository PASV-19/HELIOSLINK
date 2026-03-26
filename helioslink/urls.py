"""
URL configuration for helioslink project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from webapp import views

urlpatterns = [
    path("admin/", admin.site.urls),

    #Login/Users related
    path('', views.login_view, name='login'),
    path('crear-cuenta/', views.crear_cuenta, name='crear_cuenta'),
    path('restablecer', views.restablecer, name='restablecer'),

    #Real time page / ESP32 redirection
    path('dashboard', views.dashboard, name='dashboard'),

    #Informative pages / non real-time data
    path('graf-info/', views.graf_info_view, name='graf_info'),
    path('graf-hist/', views.graf_hist_view, name='graf_hist'),
    path('reportes/', views.reportes, name='reportes'),
    path('user-info/', views.user_info, name='user_info'),
    path('net-info/', views.net_info, name='net_info'),
]
