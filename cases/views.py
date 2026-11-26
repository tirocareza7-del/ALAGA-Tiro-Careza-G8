from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import AppUser

from .forms import CaseFilterForm, CaseForm
from .models import AnimalCase, CasePhoto

PER_PAGE = 9


def _case_queryset():
    return AnimalCase.objects.select_related("barangay", "reporter").prefetch_related(
        "photos"
    )


@role_required(AppUser.Role.USER)
def case_create(request):
    """CREATE: a resident reports an animal."""
    if request.method == "POST":
        form = CaseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                case = form.save(commit=False)
                case.reporter = request.user 
                case.save()
                for photo in form.cleaned_data["photos"]:
                    CasePhoto.objects.create(case=case, photo=photo)
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
    """READ: a resident's own cases."""
    cases = _case_queryset().filter(reporter=request.user, is_hidden=False)
    page_obj = Paginator(cases, PER_PAGE).get_page(request.GET.get("page"))
    return render(request, "cases/case_list.html", {"page_obj": page_obj})


@role_required(AppUser.Role.USER, AppUser.Role.ADMIN)
def case_community(request):
    """READ: everyone's visible cases, with filters."""
    cases = _case_queryset().filter(is_hidden=False)
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
    """READ: one case."""
    case = get_object_or_404(_case_queryset(), pk=pk)
    is_admin = request.user.role == AppUser.Role.ADMIN
    if case.is_hidden and not is_admin:
        raise Http404
    context = {
        "case": case,
        "is_owner": case.reporter_id == request.user.pk,
    }
    return render(request, "cases/case_detail.html", context)
