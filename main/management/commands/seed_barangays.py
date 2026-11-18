from django.core.management.base import BaseCommand

from main.models import Barangay

# EDIT THIS LIST: replace with your project's real pilot barangays.
PILOT_BARANGAYS = ["Lahug", "Guadalupe", "Mabolo"]


class Command(BaseCommand):
    help = "Create the pilot barangays so users can register (safe to run twice)."

    def handle(self, *args, **options):
        for name in PILOT_BARANGAYS:
            _, created = Barangay.objects.get_or_create(
                name=name, defaults={"city": "Cebu City", "is_pilot": True}
            )
            self.stdout.write(f"{'Created' if created else 'Already exists'}: {name}")
