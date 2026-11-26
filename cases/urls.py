from django.urls import path

from . import views

urlpatterns = [
    path("cases/", views.case_list, name="case_list"),
    path("cases/new/", views.case_create, name="case_create"),
    path("cases/community/", views.case_community, name="case_community"),
    path("cases/<int:pk>/", views.case_detail, name="case_detail"),
]
