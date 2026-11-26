from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import AppUser

from .forms import CaseFilterForm, CaseForm
from .models import AnimalCase, CasePhoto
from .services import (
    StatusChangeError,
    available_status_actions,
    change_case_status,
    record_creation,
)

PER_PAGE = 9


def _case_queryset():
    return AnimalCase.objects.select_related("barangay", "reporter").prefetch_related(
        "photos"
    )


def _own_case_or_404(request, pk):
    return get_object_or_404(
        AnimalCase, pk=pk, reporter=request.user, is_hidden=False
    )


@role_required(AppUser.Role.USER)
def case_create(request):
    if request.method == "POST":
        form = CaseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                case = form.save(commit=False)
                case.reporter = request.user
                case.save()
                for photo in form.cleaned_data["photos"]:
                    CasePhoto.objects.create(case=case, photo=photo)
                record_creation(case, request.user)
            messages.success(request, "Your case was posted. Thank you for helping!")
            return redirect(case)
        messages.error(request, "Please fix the errors below.")
    else:
        form = CaseForm(user=request.user)
    return render(
        request, "cases/case_form.html", {"form": form, "page_title": "Report an animal"}
    )


@role_required(AppUser.Role.USER)
def case_list(request):
    cases = _case_queryset().filter(reporter=request.user, is_hidden=False)
    page_obj = Paginator(cases, PER_PAGE).get_page(request.GET.get("page"))
    return render(request, "cases/case_list.html", {"page_obj": page_obj})


@role_required(AppUser.Role.USER, AppUser.Role.ADMIN)
def case_community(request):
    cases = _case_queryset()
    if request.user.role != AppUser.Role.ADMIN:
        cases = cases.filter(is_hidden=False)
    form = CaseFilterForm(request.GET or None)
    if form.is_valid():
        data = form.cleaned_data
        if data["q"]:
            cases = cases.filter(description__icontains=data["q"])
        if data["case_type"]:
            cases = cases.filter(case_type=data["case_type"])
        if data["urgency_level"]:
            cases = cases.filter(urgency_level=data["urgency_level"])
        if data["status"]:
            cases = cases.filter(status=data["status"])
        if data["barangay"]:
            cases = cases.filter(barangay=data["barangay"])

    params = request.GET.copy()
    params.pop("page", None)
    context = {
        "page_obj": Paginator(cases, PER_PAGE).get_page(request.GET.get("page")),
        "filter_form": form,
        "querystring": params.urlencode(),
    }
    return render(request, "cases/case_community.html", context)


@login_required
def case_detail(request, pk):
    case = get_object_or_404(_case_queryset(), pk=pk)
    is_admin = request.user.role == AppUser.Role.ADMIN
    if case.is_hidden and not is_admin:
        raise Http404
    is_owner = case.reporter_id == request.user.pk
    context = {
        "case": case,
        "is_owner": is_owner,
        "is_admin": is_admin,
        "can_edit": is_owner
        and not is_admin
        and not case.is_hidden
        and case.status != AnimalCase.Status.RESOLVED,
        "can_delete": is_owner and not is_admin and not case.is_hidden,
        "status_actions": available_status_actions(case, request.user)
        if not case.is_hidden
        else [],
        "history": case.status_history.select_related("changed_by"),
    }
    return render(request, "cases/case_detail.html", context)


@role_required(AppUser.Role.USER)
def case_edit(request, pk):
    case = _own_case_or_404(request, pk)
    if case.status == AnimalCase.Status.RESOLVED:
        messages.error(request, "Resolved cases can no longer be edited.")
        return redirect(case)

    if request.method == "POST":
        form = CaseForm(request.POST, request.FILES, instance=case, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                case = form.save()
                for photo in form.cleaned_data["remove_photos"]:
                    photo.photo.delete(save=False)
                    photo.delete()
                for photo in form.cleaned_data["photos"]:
                    CasePhoto.objects.create(case=case, photo=photo)
            messages.success(request, "Your case was updated.")
            return redirect(case)
        messages.error(request, "Please fix the errors below.")
    else:
        form = CaseForm(instance=case, user=request.user)
    return render(
        request,
        "cases/case_form.html",
        {"form": form, "page_title": f"Edit case #{case.pk}"},
    )


@role_required(AppUser.Role.USER)
def case_delete(request, pk):
    case = _own_case_or_404(request, pk)
    if request.method == "POST":
        case.is_hidden = True
        case.save(update_fields=["is_hidden"])
        messages.success(request, "Your case was removed.")
        return redirect("case_list")
    return render(request, "cases/case_confirm_delete.html", {"case": case})


@login_required
@require_POST
def case_status(request, pk):
    case = get_object_or_404(AnimalCase, pk=pk)
    if case.is_hidden:
        raise Http404
    try:
        change_case_status(case, request.POST.get("status", ""), request.user)
    except StatusChangeError as error:
        messages.error(request, str(error))
    else:
        messages.success(
            request, f"Status updated to {case.get_status_display().lower()}."
        )
    return redirect(case)


@role_required(AppUser.Role.ADMIN)
@require_POST
def case_moderate(request, pk):
    case = get_object_or_404(AnimalCase, pk=pk)
    case.is_hidden = not case.is_hidden
    case.save(update_fields=["is_hidden"])
    messages.success(
        request,
        "The case is now hidden from users." if case.is_hidden else "The case is visible again.",
    )
    return redirect(case)
