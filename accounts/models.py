"""
ALAGA models for the Account Feature (BARANGAY and APP_USER from the SDD).
More models are added in later phases.
"""
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class Barangay(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default="Cebu City")
    is_pilot = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.city}"


class AppUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("An email address is required (BR-01).")
        email = self.normalize_email(email).lower()

      
        barangay = extra_fields.pop("barangay", None)
        if barangay is not None:
            if isinstance(barangay, Barangay):
                extra_fields["barangay"] = barangay
            else:
                extra_fields["barangay_id"] = barangay

        user = self.model(email=email, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", AppUser.Role.ADMIN)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class AppUser(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        USER = "user", "Resident"
        ADMIN = "admin", "Admin"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    barangay = models.ForeignKey(
        Barangay, on_delete=models.PROTECT, related_name="users"
    ) 
    full_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True) 
   
    phone = models.CharField(max_length=20, null=True, blank=True)  
    otp_code = models.CharField(max_length=255, null=True, blank=True)
    otp_expires_at = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    is_verified = models.BooleanField(default=False) 
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )  
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AppUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "barangay"]

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE 

    @property
    def is_staff(self):
        return self.role == self.Role.ADMIN  

    def __str__(self):
        return f"{self.full_name} <{self.email}>"
