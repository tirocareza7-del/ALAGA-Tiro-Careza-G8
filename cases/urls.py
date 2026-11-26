from django.urls import path

from . import views

urlpatterns = [
    path("cases/", views.case_list, name="case_list"),
    path("cases/new/", views.case_create, name="case_create"),
    path("cases/community/", views.case_community, name="case_community"),
    path("cases/<int:pk>/", views.case_detail, name="case_detail"),
    path("cases/<int:pk>/edit/", views.case_edit, name="case_edit"),
    path("cases/<int:pk>/delete/", views.case_delete, name="case_delete"),
    path("cases/<int:pk>/status/", views.case_status, name="case_status"),
    path("cases/<int:pk>/moderate/", views.case_moderate, name="case_moderate"),
]
