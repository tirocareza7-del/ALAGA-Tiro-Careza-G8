from django.contrib import admin

from .models import AnimalCase, CasePhoto


class CasePhotoInline(admin.TabularInline):
    model = CasePhoto
    extra = 0
    max_num = 3  # BR-07


@admin.register(AnimalCase)
class AnimalCaseAdmin(admin.ModelAdmin):
    list_display = ["id", "case_type", "animal_type", "urgency_level", "status",
                    "barangay", "reporter", "is_hidden", "posted_at"]
    list_filter = ["case_type", "status", "urgency_level", "is_hidden", "barangay"]
    search_fields = ["description"]
    readonly_fields = ["posted_at"]
    inlines = [CasePhotoInline]
