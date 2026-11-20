from django.core.management.base import BaseCommand

from appointments import services


class Command(BaseCommand):
    help = "Remove stale booking slots and report active appointments that are missing slots."

    def handle(self, *args, **options):
        result = services.repair_slots()
        self.stdout.write(f"Removed {result['removed']} stale slot(s).")
        if result["missing"]:
            self.stdout.write(self.style.WARNING(
                f"{result['missing']} slot(s) missing for active appointments. Review these manually."
            ))
        else:
            self.stdout.write(self.style.SUCCESS("No missing slots."))
