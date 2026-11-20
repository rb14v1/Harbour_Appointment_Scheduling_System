from datetime import timedelta

from .base import MongoApiTestCase, future_time


class AppointmentRulesTests(MongoApiTestCase):
    def setUp(self):
        super().setUp()
        self.customer_id = self.create_customer()
        self.type_id = self.create_type()

    def book_ok(self, start, minutes=60, **extra):
        response = self.book(self.customer_id, self.type_id, start, minutes, **extra)
        self.assertEqual(response.status_code, 201, response.json())
        return response.json()

    def test_create_appointment_with_derived_fields(self):
        start = future_time(days=3, hour=10)
        appointment = self.book_ok(start, description="Initial review")
        self.assertEqual(appointment["status"], "scheduled")
        self.assertEqual(appointment["customer_name"], "Jane Doe")
        self.assertEqual(appointment["appointment_type_name"], "Consultation")
        self.assertEqual(appointment["description"], "Initial review")
        self.assertRegex(appointment["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_end_must_be_later_than_start(self):
        start = future_time()
        response = self.book(self.customer_id, self.type_id, start, minutes=0)
        self.assertEqual(response.status_code, 400)

    def test_times_must_align_to_15_minutes(self):
        start = future_time().replace(minute=10)
        response = self.book(self.customer_id, self.type_id, start)
        self.assertEqual(response.status_code, 400)

    def test_past_appointments_are_rejected(self):
        start = future_time(days=-2)
        response = self.book(self.customer_id, self.type_id, start)
        self.assertEqual(response.status_code, 400)

    def test_unknown_customer_is_rejected(self):
        response = self.book("000000000000000000000000", self.type_id, future_time())
        self.assertEqual(response.status_code, 400)

    def test_cancelled_appointment_frees_its_slots(self):
        appointment = self.book_ok(future_time(hour=9))
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 409)

        cancel = self.api.post(f"/api/appointments/{appointment['id']}/cancel/", format="json")
        self.assertEqual(cancel.json()["status"], "cancelled")
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 201)

    def test_completed_appointment_keeps_blocking_its_slots(self):
        appointment = self.book_ok(future_time(hour=9))
        self.api.post(f"/api/appointments/{appointment['id']}/complete/", format="json")
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 409)

    def test_only_scheduled_appointments_can_be_completed_or_cancelled(self):
        appointment = self.book_ok(future_time())
        url = f"/api/appointments/{appointment['id']}"
        self.assertEqual(self.api.post(f"{url}/complete/", format="json").status_code, 200)
        self.assertEqual(self.api.post(f"{url}/complete/", format="json").status_code, 409)
        self.assertEqual(self.api.post(f"{url}/cancel/", format="json").status_code, 409)

    def test_completed_appointment_cannot_be_rescheduled(self):
        appointment = self.book_ok(future_time(hour=9))
        self.api.post(f"/api/appointments/{appointment['id']}/complete/", format="json")
        response = self.api.post(
            f"/api/appointments/{appointment['id']}/reschedule/",
            {"start_at": future_time(hour=11).isoformat(), "end_at": future_time(hour=12).isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, 409)

    def test_reschedule_moves_slots(self):
        appointment = self.book_ok(future_time(hour=9))
        new_start = future_time(hour=14)
        response = self.api.post(
            f"/api/appointments/{appointment['id']}/reschedule/",
            {"start_at": new_start.isoformat(), "end_at": (new_start + timedelta(hours=1)).isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 201)
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=14)).status_code, 409)

    def test_reschedule_into_conflict_returns_409_and_keeps_original_slots(self):
        original = self.book_ok(future_time(hour=9))
        self.book_ok(future_time(hour=11))
        response = self.api.post(
            f"/api/appointments/{original['id']}/reschedule/",
            {"start_at": future_time(hour=11).isoformat(), "end_at": future_time(hour=12).isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, 409)

        stored = self.api.get(f"/api/appointments/{original['id']}/").json()
        self.assertEqual(stored["start_at"], future_time(hour=9).isoformat().replace("+00:00", "Z"))
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 409)

    def test_patch_rejects_time_fields(self):
        appointment = self.book_ok(future_time())
        response = self.api.patch(
            f"/api/appointments/{appointment['id']}/",
            {"start_at": future_time(hour=15).isoformat()},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_updates_description_for_any_status(self):
        appointment = self.book_ok(future_time())
        self.api.post(f"/api/appointments/{appointment['id']}/complete/", format="json")
        response = self.api.patch(
            f"/api/appointments/{appointment['id']}/",
            {"description": "Follow-up notes"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["description"], "Follow-up notes")

    def test_list_filters_by_status_and_date(self):
        first = self.book_ok(future_time(days=2, hour=9))
        self.book_ok(future_time(days=5, hour=9))
        self.api.post(f"/api/appointments/{first['id']}/cancel/", format="json")

        cancelled = self.api.get("/api/appointments/?status=cancelled").json()
        self.assertEqual([a["id"] for a in cancelled], [first["id"]])

        in_range = self.api.get(f"/api/appointments/?date_from={first['date']}&date_to={first['date']}").json()
        self.assertEqual(len(in_range), 1)

    def test_invalid_filter_returns_400(self):
        response = self.api.get("/api/appointments/?status=unknown")
        self.assertEqual(response.status_code, 400)
