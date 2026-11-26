from decimal import Decimal

from django import forms
from django.utils import timezone

from accounts.models import Barangay

from .models import AnimalCase

MAX_PHOTOS = 3                     
MAX_PHOTO_MB = 5
MAX_CASES_PER_DAY = 10            

PILOT_MIN_LAT, PILOT_MAX_LAT = 10.20, 10.50
PILOT_MIN_LNG, PILOT_MAX_LNG = 123.70, 124.00


def add_bootstrap_classes(form):
    for field in form.fields.values():
        if isinstance(field.widget, forms.Select):
            css = "form-select"
        elif isinstance(field.widget, forms.ClearableFileInput):
            css = "form-control"
        else:
            css = "form-control"
        field.widget.attrs["class"] = css


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """An image field that accepts several files at once."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data if d]
        return [single(data, initial)] if data else []


class CaseForm(forms.ModelForm):
    barangay = forms.ModelChoiceField(
        queryset=Barangay.objects.filter(is_pilot=True),
        empty_label="Select a barangay",
    )
    photos = MultipleImageField(
        required=False,
        label="Photos",
        help_text=f"Upload 1 to {MAX_PHOTOS} photos (max {MAX_PHOTO_MB} MB each).",
    )

    class Meta:
        model = AnimalCase
        fields = [
            "barangay", "case_type", "animal_type", "urgency_level",
            "description", "latitude", "longitude", "address_note",
        ]
        labels = {
            "case_type": "What happened?",
            "animal_type": "Animal",
            "urgency_level": "Urgency",
            "address_note": "Landmark or address hint",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        add_bootstrap_classes(self)
        self.fields["case_type"].choices = [("", "Select...")] + list(
            AnimalCase.CaseType.choices
        )
        self.fields["animal_type"].choices = [("", "Select...")] + list(
            AnimalCase.AnimalType.choices
        )
        self.fields["urgency_level"].choices = [("", "Select...")] + list(
            AnimalCase.Urgency.choices
        )
        if user and not self.instance.pk:
            self.fields["barangay"].initial = user.barangay_id

    def clean_description(self):
        text = self.cleaned_data["description"].strip()
        if len(text) < 10:
            raise forms.ValidationError(
                "Please describe the situation in at least 10 characters."
            )
        return text

    def clean_photos(self):
        photos = [p for p in (self.cleaned_data.get("photos") or []) if p]
        if not photos and not self.instance.pk:
            raise forms.ValidationError("Please upload at least 1 photo (BR-07).")
        if len(photos) > MAX_PHOTOS:
            raise forms.ValidationError(f"You can upload at most {MAX_PHOTOS} photos.")
        for p in photos:
            if p.size > MAX_PHOTO_MB * 1024 * 1024:
                raise forms.ValidationError(
                    f"'{p.name}' is larger than {MAX_PHOTO_MB} MB."
                )
        return photos

    def clean(self):
        cleaned = super().clean()

        lat, lng = cleaned.get("latitude"), cleaned.get("longitude")
        if lat is not None and lng is not None:
            if not (
                PILOT_MIN_LAT <= float(lat) <= PILOT_MAX_LAT
                and PILOT_MIN_LNG <= float(lng) <= PILOT_MAX_LNG
            ):
                self.add_error(
                    "latitude",
                    "The pin must be inside the pilot area (Cebu City). "
                    "Click the map to place it.",
                )

        
        if self.user and not self.instance.pk:
            start_of_day = timezone.localtime().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            posted_today = AnimalCase.objects.filter(
                reporter=self.user, posted_at__gte=start_of_day
            ).count()
            if posted_today >= MAX_CASES_PER_DAY:
                raise forms.ValidationError(
                    f"You have reached the limit of {MAX_CASES_PER_DAY} case posts per day."
                )
        return cleaned


class CaseFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search", widget=forms.TextInput(
        attrs={"placeholder": "Search descriptions..."}))
    case_type = forms.ChoiceField(
        required=False, label="Type",
        choices=[("", "All types")] + list(AnimalCase.CaseType.choices))
    urgency_level = forms.ChoiceField(
        required=False, label="Urgency",
        choices=[("", "Any urgency")] + list(AnimalCase.Urgency.choices))
    status = forms.ChoiceField(
        required=False, label="Status",
        choices=[("", "Any status")] + list(AnimalCase.Status.choices))
    barangay = forms.ModelChoiceField(
        required=False, label="Barangay", empty_label="All barangays",
        queryset=Barangay.objects.filter(is_pilot=True))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            )
