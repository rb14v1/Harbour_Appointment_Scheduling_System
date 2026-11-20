from .base import MongoApiTestCase, future_time


class CustomerApiTests(MongoApiTestCase):
    def test_create_and_fetch_customer(self):
        response = self.api.post(
            "/api/customers/",
            {"full_name": "Jane Doe", "email": "Jane@Example.com", "phone": "0700", "address": "1 Quay St"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        customer = response.json()
        self.assertEqual(customer["email"], "jane@example.com")
        self.assertTrue(customer["created_at"].endswith("Z"))

        detail = self.api.get(f"/api/customers/{customer['id']}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["full_name"], "Jane Doe")

    def test_invalid_email_returns_400(self):
        response = self.api.post(
            "/api/customers/",
            {"full_name": "Jane", "email": "not-an-email", "phone": "0700"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "validation_error")

    def test_duplicate_email_returns_409(self):
        self.create_customer(email="jane@example.com")
        response = self.api.post(
            "/api/customers/",
            {"full_name": "Other", "email": "JANE@example.com", "phone": "0701"},
            format="json",
        )
        self.assertEqual(response.status_code, 409)

    def test_search_matches_name_email_and_phone(self):
        self.create_customer(email="jane@example.com", full_name="Jane Doe")
        self.create_customer(email="bob@example.com", full_name="Bob Smith")

        self.assertEqual(len(self.api.get("/api/customers/?search=jane").json()), 1)
        self.assertEqual(len(self.api.get("/api/customers/?search=bob@ex").json()), 1)
        self.assertEqual(len(self.api.get("/api/customers/?search=900123").json()), 2)
        self.assertEqual(len(self.api.get("/api/customers/?search=.*").json()), 0)

    def test_patch_updates_only_given_fields(self):
        customer_id = self.create_customer()
        response = self.api.patch(f"/api/customers/{customer_id}/", {"phone": "0799"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["phone"], "0799")
        self.assertEqual(response.json()["full_name"], "Jane Doe")

    def test_delete_customer_without_appointments(self):
        customer_id = self.create_customer()
        self.assertEqual(self.api.delete(f"/api/customers/{customer_id}/").status_code, 204)
        self.assertEqual(self.api.get(f"/api/customers/{customer_id}/").status_code, 404)

    def test_delete_customer_with_appointments_returns_409(self):
        customer_id = self.create_customer()
        type_id = self.create_type()
        self.assertEqual(self.book(customer_id, type_id, future_time()).status_code, 201)
        response = self.api.delete(f"/api/customers/{customer_id}/")
        self.assertEqual(response.status_code, 409)

    def test_unknown_customer_returns_404(self):
        self.assertEqual(self.api.get("/api/customers/000000000000000000000000/").status_code, 404)
        self.assertEqual(self.api.get("/api/customers/not-an-id/").status_code, 404)
