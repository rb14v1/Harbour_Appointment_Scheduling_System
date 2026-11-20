import threading

from django.conf import settings
from pymongo import MongoClient

CUSTOMERS = "customers"
APPOINTMENT_TYPES = "appointment_types"
APPOINTMENTS = "appointments"
APPOINTMENT_SLOTS = "appointment_slots"

_client = None
_client_lock = threading.Lock()


def get_client():
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = MongoClient(
                    settings.MONGO_URI,
                    tz_aware=True,
                    serverSelectionTimeoutMS=5000,
                )
    return _client


def get_db():
    return get_client()[settings.MONGO_DB_NAME]
