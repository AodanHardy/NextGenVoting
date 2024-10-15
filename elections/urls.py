from django.urls import path, include
from django.contrib.auth import views as auth_views

import elections
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
