from django.db import transaction
from django.utils import timezone

from accounts.models import AppUser

from .models import AnimalCase, CaseStatusHistory

Status = AnimalCase.Status

NEXT_STATUS = {
    Status.OPEN: Status.BEING_HANDLED,
    Status.BEING_HANDLED: Status.RESOLVED,
}


class StatusChangeError(Exception):
    pass


def can_change_status(case, user):
    if user.role == AppUser.Role.ADMIN:
        return True
    return user.pk == case.reporter_id


def available_status_actions(case, user):
    if not can_change_status(case, user):
        return []
    if user.role == AppUser.Role.ADMIN and case.status == Status.RESOLVED:
        return [(Status.OPEN, "Reopen case", "btn-outline-secondary")]
    if case.status == Status.OPEN:
        return [(Status.BEING_HANDLED, "Mark as being handled", "btn-info")]
    if case.status == Status.BEING_HANDLED:
        return [(Status.RESOLVED, "Mark as resolved", "btn-success")]
    return []


def record_creation(case, user):
    return CaseStatusHistory.objects.create(
        case=case, changed_by=user, old_status=None, new_status=case.status
    )


@transaction.atomic
def change_case_status(case, new_status, user):
    if new_status not in Status.values:
        raise StatusChangeError("That is not a valid status.")
    if new_status == case.status:
        raise StatusChangeError("The case already has that status.")
    if not can_change_status(case, user):
        raise StatusChangeError("You are not allowed to change the status of this case.")

    is_admin = user.role == AppUser.Role.ADMIN
    if not is_admin and NEXT_STATUS.get(case.status) != new_status:
        raise StatusChangeError(
            "A case can only move from open to being handled to resolved."
        )

    old_status = case.status
    case.status = new_status
    case.resolved_at = timezone.now() if new_status == Status.RESOLVED else None
    case.save(update_fields=["status", "resolved_at"])
    CaseStatusHistory.objects.create(
        case=case, changed_by=user, old_status=old_status, new_status=new_status
    )
    return case
