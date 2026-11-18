from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppUser, Barangay


@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "is_pilot"]
    list_filter = ["is_pilot"]


@admin.register(AppUser)
class AppUserAdmin(UserAdmin):
    ordering = ["email"]
    list_display = ["email", "full_name", "barangay", "role", "status", "is_verified"]
    list_filter = ["role", "status", "is_verified", "barangay"]
    search_fields = ["email", "full_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("full_name", "phone", "barangay")}),
        ("Access", {"fields": ("role", "status", "is_verified", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "barangay", "password1", "password2"),
            },
        ),
    )
    filter_horizontal = []
