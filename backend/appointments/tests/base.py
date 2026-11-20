from datetime import timedelta

from django.conf import settings
from django.test import SimpleTestCase
from rest_framework.test import APIClient

from appointments.mongo import APPOINTMENT_SLOTS, APPOINTMENT_TYPES, APPOINTMENTS, CUSTOMERS, get_db
from appointments.timeutils import now_utc
from mongo_migrations.runner import apply_pending


def future_time(days=2, hour=9, minute=0):
    base = now_utc() + timedelta(days=days)
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def appointment_payload(customer_id, type_id, start, minutes=60, **extra):
    return {
        "customer_id": customer_id,
        "appointment_type_id": type_id,
        "start_at": start.isoformat(),
        "end_at": (start + timedelta(minutes=minutes)).isoformat(),
        **extra,
    }


class MongoApiTestCase(SimpleTestCase):
    """Runs against a real MongoDB database. Only collections of a *_test database are cleared."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not settings.MONGO_DB_NAME.endswith("_test"):
            raise RuntimeError("Refusing to run tests: MONGO_DB_NAME must end with '_test'.")
        apply_pending(get_db())

    def setUp(self):
        super().setUp()
        self.api = APIClient()
        db = get_db()
        for name in (CUSTOMERS, APPOINTMENT_TYPES, APPOINTMENTS, APPOINTMENT_SLOTS):
            db[name].delete_many({})

    def create_customer(self, email="jane@example.com", full_name="Jane Doe"):
        response = self.api.post(
            "/api/customers/",
            {"full_name": full_name, "email": email, "phone": "+44 7700 900123"},
            format="json",
        )
        assert response.status_code == 201, response.json()
        return response.json()["id"]

    def create_type(self, name="Consultation", duration_minutes=60):
        response = self.api.post(
            "/api/appointment-types/",
            {"name": name, "description": "", "duration_minutes": duration_minutes},
            format="json",
        )
        assert response.status_code == 201, response.json()
        return response.json()["id"]

    def book(self, customer_id, type_id, start, minutes=60, **extra):
        return self.api.post(
            "/api/appointments/",
            appointment_payload(customer_id, type_id, start, minutes, **extra),
            format="json",
        )
