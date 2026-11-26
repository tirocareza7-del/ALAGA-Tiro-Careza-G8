from django.contrib import admin

from .models import AnimalCase, CasePhoto, CaseStatusHistory


class CasePhotoInline(admin.TabularInline):
    model = CasePhoto
    extra = 0
    max_num = 3


@admin.register(AnimalCase)
class AnimalCaseAdmin(admin.ModelAdmin):
    list_display = ["id", "case_type", "animal_type", "urgency_level", "status",
                    "barangay", "reporter", "is_hidden", "posted_at"]
    list_filter = ["case_type", "status", "urgency_level", "is_hidden", "barangay"]
    search_fields = ["description"]
    readonly_fields = ["posted_at"]
    inlines = [CasePhotoInline]


@admin.register(CaseStatusHistory)
class CaseStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["case", "old_status", "new_status", "changed_by", "changed_at"]
    list_filter = ["new_status"]
