from django.core.management.base import BaseCommand, CommandError
from pymongo.errors import OperationFailure

from appointments.mongo import get_db
from mongo_migrations.runner import apply_pending, applied_versions, discover


class Command(BaseCommand):
    help = "Apply pending MongoDB migrations. Use --status to list them without applying."

    def add_arguments(self, parser):
        parser.add_argument("--status", action="store_true", help="List migrations and whether they are applied.")

    def handle(self, *args, **options):
        db = get_db()

        if options["status"]:
            done = applied_versions(db)
            for module in discover():
                mark = "x" if module.VERSION in done else " "
                self.stdout.write(f"[{mark}] {module.VERSION} - {module.DESCRIPTION}")
            return

        try:
            applied = apply_pending(db)
        except OperationFailure as exc:
            raise CommandError(f"Migration failed: {exc}") from exc

        if applied:
            for version in applied:
                self.stdout.write(self.style.SUCCESS(f"Applied {version}"))
        else:
            self.stdout.write("No pending migrations.")
