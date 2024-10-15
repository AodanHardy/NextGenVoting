from django.urls import path, include
from django.contrib.auth import views as auth_views

import elections
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]
