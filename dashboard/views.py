from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import AppUser


def home(request):
    return redirect("dashboard")


@login_required
def dashboard(request):
    """Send each user to the dashboard for their role."""
    if request.user.role == AppUser.Role.ADMIN:
        return redirect("admin_dashboard")
    return redirect("resident_dashboard")


@role_required(AppUser.Role.USER)
def resident_dashboard(request):
    return render(request, "dashboards/resident.html")


@role_required(AppUser.Role.ADMIN)
def admin_dashboard(request):
    context = {
        "total_users": AppUser.objects.count(),
        "resident_count": AppUser.objects.filter(role=AppUser.Role.USER).count(),
        "admin_count": AppUser.objects.filter(role=AppUser.Role.ADMIN).count(),
        "suspended_count": AppUser.objects.filter(
            status=AppUser.Status.SUSPENDED
        ).count(),
        "recent_users": AppUser.objects.select_related("barangay").order_by(
            "-created_at"
        )[:5],
    }
    return render(request, "dashboards/admin.html", context)
