from .base import MongoApiTestCase, future_time


class AppointmentTypeApiTests(MongoApiTestCase):
    def test_create_list_and_patch_type(self):
        type_id = self.create_type("Follow-up", duration_minutes=30)
        self.assertEqual(len(self.api.get("/api/appointment-types/").json()), 1)

        response = self.api.patch(
            f"/api/appointment-types/{type_id}/", {"is_active": False}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_active"])
        self.assertEqual(response.json()["duration_minutes"], 30)

    def test_duplicate_name_returns_409(self):
        self.create_type("Meeting")
        response = self.api.post(
            "/api/appointment-types/",
            {"name": "Meeting", "duration_minutes": 60},
            format="json",
        )
        self.assertEqual(response.status_code, 409)

    def test_duration_must_be_multiple_of_15(self):
        response = self.api.post(
            "/api/appointment-types/",
            {"name": "Odd", "duration_minutes": 50},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_unused_type(self):
        type_id = self.create_type()
        self.assertEqual(self.api.delete(f"/api/appointment-types/{type_id}/").status_code, 204)

    def test_delete_type_in_use_returns_409(self):
        customer_id = self.create_customer()
        type_id = self.create_type()
        self.assertEqual(self.book(customer_id, type_id, future_time()).status_code, 201)
        self.assertEqual(self.api.delete(f"/api/appointment-types/{type_id}/").status_code, 409)

    def test_inactive_type_cannot_be_booked(self):
        customer_id = self.create_customer()
        type_id = self.create_type()
        self.api.patch(f"/api/appointment-types/{type_id}/", {"is_active": False}, format="json")
        response = self.book(customer_id, type_id, future_time())
        self.assertEqual(response.status_code, 400)
