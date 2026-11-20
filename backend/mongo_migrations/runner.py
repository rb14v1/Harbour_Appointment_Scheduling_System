import importlib
import pkgutil
from datetime import datetime, timezone

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

SCHEMA_MIGRATIONS = "schema_migrations"


def discover():
    """Return migration modules sorted by filename (0001_..., 0002_..., ...)."""
    package = importlib.import_module(__package__)
    names = sorted(m.name for m in pkgutil.iter_modules(package.__path__) if m.name[:4].isdigit())
    modules = []
    for name in names:
        module = importlib.import_module(f"{__package__}.{name}")
        for attribute in ("VERSION", "DESCRIPTION", "up"):
            if not hasattr(module, attribute):
                raise RuntimeError(f"Migration {name} is missing {attribute}.")
        modules.append(module)
    return modules


def applied_versions(db):
    return {doc["version"] for doc in db[SCHEMA_MIGRATIONS].find({}, {"version": 1})}


def apply_pending(db):
    """Apply every migration not yet recorded. Returns the versions applied in this call."""
    ledger = db[SCHEMA_MIGRATIONS]
    ledger.create_index([("version", ASCENDING)], unique=True, name="uniq_version")

    done = applied_versions(db)
    applied = []
    for module in discover():
        if module.VERSION in done:
            continue
        module.up(db)
        try:
            ledger.insert_one(
                {
                    "version": module.VERSION,
                    "description": module.DESCRIPTION,
                    "applied_at": datetime.now(timezone.utc),
                }
            )
        except DuplicateKeyError:
            # Another process recorded it first. Migrations are idempotent, so this is safe.
            pass
        applied.append(module.VERSION)
    return applied
