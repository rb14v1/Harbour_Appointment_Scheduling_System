from datetime import timedelta

from appointments.timeutils import local_date_string, now_utc

from .base import MongoApiTestCase, future_time


class DashboardTests(MongoApiTestCase):
    def test_dashboard_counts_and_type_statistics(self):
        customer_id = self.create_customer()
        consultation = self.create_type("Consultation")
        meeting = self.create_type("Meeting")

        completed = self.book(customer_id, consultation, future_time(days=2, hour=9)).json()
        cancelled = self.book(customer_id, consultation, future_time(days=2, hour=10)).json()
        self.book(customer_id, meeting, future_time(days=3, hour=9))
        self.book(customer_id, consultation, future_time(days=4, hour=9))

        self.api.post(f"/api/appointments/{completed['id']}/complete/", format="json")
        self.api.post(f"/api/appointments/{cancelled['id']}/cancel/", format="json")

        data = self.api.get("/api/dashboard/").json()
        self.assertEqual(data["total"], 4)
        self.assertEqual(data["completed"], 1)
        self.assertEqual(data["cancelled"], 1)
        self.assertEqual(data["upcoming"], 2)

        counts = {row["type_name"]: row["count"] for row in data["by_type"]}
        self.assertEqual(counts, {"Consultation": 3, "Meeting": 1})

        self.assertEqual(len(data["recent"]), 4)
        self.assertEqual(data["recent"][0]["customer_name"], "Jane Doe")

    def test_today_counts_non_cancelled_appointments_on_local_date(self):
        now = now_utc()
        start = (now + timedelta(minutes=30)).replace(second=0, microsecond=0)
        start += timedelta(minutes=(15 - start.minute % 15) % 15)
        if local_date_string(start) != local_date_string(now):
            self.skipTest("Local day changes within the next 30 minutes.")

        customer_id = self.create_customer()
        type_id = self.create_type()
        self.assertEqual(self.book(customer_id, type_id, start).status_code, 201)

        self.assertEqual(self.api.get("/api/dashboard/").json()["today"], 1)
