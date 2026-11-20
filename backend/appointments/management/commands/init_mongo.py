from django.core.management.base import BaseCommand, CommandError
from pymongo.errors import OperationFailure

from appointments.mongo import get_db
from mongo_migrations.runner import apply_pending


class Command(BaseCommand):
    help = "Apply pending MongoDB migrations. Safe to re-run; never deletes data."

    def handle(self, *args, **options):
        db = get_db()
        self.stdout.write(f"Database: {db.name}")
        try:
            applied = apply_pending(db)
        except OperationFailure as exc:
            raise CommandError(
                "A migration failed. Existing documents may violate a unique index; "
                f"resolve the duplicates manually and re-run. Detail: {exc}"
            ) from exc
        if applied:
            for version in applied:
                self.stdout.write(f"Applied {version}")
        else:
            self.stdout.write("Database is up to date.")
        self.stdout.write(self.style.SUCCESS("Done."))
