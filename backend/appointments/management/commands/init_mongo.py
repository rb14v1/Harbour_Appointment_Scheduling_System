import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from pymongo.uri_parser import parse_uri

from appointments.mongo import get_db
from mongo_migrations.runner import apply_pending

REPLICA_SET_NAME = "rs0"
NOT_YET_INITIALIZED = 94
PRIMARY_WAIT_SECONDS = 30


def _direct_client():
    host, port = parse_uri(settings.MONGO_URI)["nodelist"][0]
    return MongoClient(host, port, directConnection=True, serverSelectionTimeoutMS=5000)


def _initiate_if_needed(client):
    try:
        client.admin.command("replSetGetStatus")
        return False
    except OperationFailure as exc:
        if exc.code != NOT_YET_INITIALIZED:
            raise
    host, port = parse_uri(settings.MONGO_URI)["nodelist"][0]
    client.admin.command(
        "replSetInitiate",
        {"_id": REPLICA_SET_NAME, "members": [{"_id": 0, "host": f"{host}:{port}"}]},
    )
    return True


def _wait_for_primary(client):
    deadline = time.monotonic() + PRIMARY_WAIT_SECONDS
    while time.monotonic() < deadline:
        if client.admin.command("hello").get("isWritablePrimary"):
            return
        time.sleep(0.5)
    raise CommandError("The replica set did not elect a primary in time. Check the mongod log.")


class Command(BaseCommand):
    help = "Initialise the local replica set if needed, then apply pending migrations. Safe to re-run."

    def handle(self, *args, **options):
        client = _direct_client()
        try:
            if _initiate_if_needed(client):
                self.stdout.write(f"Replica set '{REPLICA_SET_NAME}' initialised.")
            _wait_for_primary(client)
        finally:
            client.close()

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
