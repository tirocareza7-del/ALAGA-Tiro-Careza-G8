from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EmailLoginForm

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            authentication_form=EmailLoginForm, redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("logout/", views.logout_view, name="logout"),
]
