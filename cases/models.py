from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse

from accounts.models import Barangay


class AnimalCase(models.Model):
    class CaseType(models.TextChoices):
        NEEDS_HELP = "needs_help", "Needs help"
        LOST = "lost", "Lost"
        FOUND = "found", "Found"

    class AnimalType(models.TextChoices):
        DOG = "dog", "Dog"
        CAT = "cat", "Cat"
        LIVESTOCK = "livestock", "Livestock"
        OTHER = "other", "Other"

    class Urgency(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        BEING_HANDLED = "being_handled", "Being handled"
        RESOLVED = "resolved", "Resolved"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cases"
    )
    barangay = models.ForeignKey(
        Barangay, on_delete=models.PROTECT, related_name="cases"
    )
    case_type = models.CharField(max_length=20, choices=CaseType.choices)
    animal_type = models.CharField(max_length=50, choices=AnimalType.choices)
    description = models.TextField()
    urgency_level = models.CharField(max_length=20, choices=Urgency.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OPEN
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address_note = models.CharField(max_length=255, null=True, blank=True)
    is_hidden = models.BooleanField(default=False)
    posted_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-posted_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(latitude__gte=-90) & Q(latitude__lte=90),
                name="case_latitude_range",
            ),
            models.CheckConstraint(
                condition=Q(longitude__gte=-180) & Q(longitude__lte=180),
                name="case_longitude_range",
            ),
        ]

    def __str__(self):
        return f"#{self.pk} {self.get_case_type_display()} - {self.get_animal_type_display()}"

    def get_absolute_url(self):
        return reverse("case_detail", args=[self.pk])

    @property
    def urgency_badge(self):
        return {
            "low": "bg-success",
            "medium": "bg-warning text-dark",
            "high": "bg-orange text-white",
            "critical": "bg-danger",
        }.get(self.urgency_level, "bg-secondary")

    @property
    def status_badge(self):
        return {
            "open": "bg-primary",
            "being_handled": "bg-info text-dark",
            "resolved": "bg-secondary",
        }.get(self.status, "bg-secondary")


class CasePhoto(models.Model):
    case = models.ForeignKey(
        AnimalCase, on_delete=models.CASCADE, related_name="photos"
    )
    photo = models.ImageField(upload_to="case_photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.pk} of case {self.case_id}"


class CaseStatusHistory(models.Model):
    case = models.ForeignKey(
        AnimalCase, on_delete=models.CASCADE, related_name="status_history"
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="case_status_changes",
    )
    old_status = models.CharField(
        max_length=20, choices=AnimalCase.Status.choices, null=True, blank=True
    )
    new_status = models.CharField(max_length=20, choices=AnimalCase.Status.choices)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["changed_at", "pk"]
        verbose_name_plural = "case status history"

    def __str__(self):
        return f"Case {self.case_id}: {self.old_status} to {self.new_status}"
