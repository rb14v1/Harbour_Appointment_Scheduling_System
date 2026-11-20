from io import StringIO

from django.core.management import call_command

from appointments.mongo import APPOINTMENT_SLOTS, get_db
from mongo_migrations.runner import SCHEMA_MIGRATIONS, apply_pending, applied_versions, discover

from .base import MongoApiTestCase


class MigrationTests(MongoApiTestCase):
    def test_every_migration_is_recorded_once(self):
        db = get_db()
        apply_pending(db)
        apply_pending(db)

        versions = [doc["version"] for doc in db[SCHEMA_MIGRATIONS].find()]
        for module in discover():
            self.assertEqual(versions.count(module.VERSION), 1)
        self.assertEqual(apply_pending(db), [])

    def test_initial_schema_creates_the_slot_guard(self):
        apply_pending(get_db())
        indexes = get_db()[APPOINTMENT_SLOTS].index_information()
        self.assertTrue(indexes["uniq_slot"]["unique"])

    def test_status_lists_applied_migrations(self):
        apply_pending(get_db())
        out = StringIO()
        call_command("migrate_mongo", "--status", stdout=out)
        for module in discover():
            self.assertIn(module.VERSION, out.getvalue())
        self.assertIn("[x] 0001_initial_schema", out.getvalue())
        self.assertIn("0001_initial_schema", applied_versions(get_db()))

    def test_migrate_command_is_safe_to_rerun(self):
        out = StringIO()
        call_command("migrate_mongo", stdout=out)
        call_command("migrate_mongo", stdout=out)
        self.assertIn("No pending migrations.", out.getvalue())
