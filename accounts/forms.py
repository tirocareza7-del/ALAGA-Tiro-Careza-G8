from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator

from .models import AppUser, Barangay


def add_bootstrap_classes(form):
    """Give every widget a Bootstrap look."""
    for field in form.fields.values():
        css = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
        field.widget.attrs["class"] = css


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    barangay = forms.ModelChoiceField(
        queryset=Barangay.objects.filter(is_pilot=True),
        empty_label="Select your barangay",
    )  # BR-04: exactly one pilot barangay
    phone = forms.CharField(
        required=False,
        max_length=20,
        validators=[RegexValidator(r"^\+?[0-9\s-]{7,20}$", "Enter a valid phone number.")],
    )

    class Meta:
        model = AppUser
        fields = ["full_name", "email", "phone", "barangay"]
        labels = {"full_name": "Full name", "email": "Email"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if AppUser.objects.filter(email__iexact=email).exists():  # BR-01
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("The two password fields didn't match.")
        return p2

    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get("password2")
        if password:  # BR-02: min 8 characters and other Django validators
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # hashed, never plain text
        if commit:
            user.save()
        return user


class EmailLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"autofocus": True})
    )
    error_messages = {
        "invalid_login": "Invalid email or password. Please try again.",
        "inactive": "This account is suspended.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(
        required=False,
        max_length=20,
        validators=[RegexValidator(r"^\+?[0-9\s-]{7,20}$", "Enter a valid phone number.")],
    )

    class Meta:
        model = AppUser
        fields = ["full_name", "email", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_classes(self)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        taken = AppUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email