from django.urls import path, include
from django.contrib.auth import views as auth_views

import elections
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('voting', views.voting_info, name='voting-info'),
    # Login and logout views
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Signup view
    path('signup/', views.signup, name='signup'),

]
