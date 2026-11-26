from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from accounts.models import AppUser
from cases.models import AnimalCase


def home(request):
    return redirect("dashboard")


@login_required
def dashboard(request):
    if request.user.role == AppUser.Role.ADMIN:
        return redirect("admin_dashboard")
    return redirect("resident_dashboard")


@role_required(AppUser.Role.USER)
def resident_dashboard(request):
    mine = AnimalCase.objects.filter(reporter=request.user, is_hidden=False)
    context = {
        "my_total": mine.count(),
        "my_open": mine.filter(status=AnimalCase.Status.OPEN).count(),
        "my_handled": mine.filter(status=AnimalCase.Status.BEING_HANDLED).count(),
        "my_resolved": mine.filter(status=AnimalCase.Status.RESOLVED).count(),
        "recent_cases": mine.select_related("barangay").prefetch_related("photos")[:3],
    }
    return render(request, "dashboards/resident.html", context)


@role_required(AppUser.Role.ADMIN)
def admin_dashboard(request):
    cases = AnimalCase.objects.all()
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
        "case_total": cases.filter(is_hidden=False).count(),
        "case_open": cases.filter(is_hidden=False, status=AnimalCase.Status.OPEN).count(),
        "case_handled": cases.filter(
            is_hidden=False, status=AnimalCase.Status.BEING_HANDLED
        ).count(),
        "case_resolved": cases.filter(
            is_hidden=False, status=AnimalCase.Status.RESOLVED
        ).count(),
        "case_hidden": cases.filter(is_hidden=True).count(),
        "recent_cases": cases.select_related("barangay", "reporter")[:5],
    }
    return render(request, "dashboards/admin.html", context)
