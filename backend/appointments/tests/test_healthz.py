from .base import MongoApiTestCase


class HealthzTests(MongoApiTestCase):
    def test_healthz_reports_database_ok(self):
        response = self.api.get("/api/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "database": "ok"})
