from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from rest_framework.test import APIClient

from .base import MongoApiTestCase, appointment_payload, future_time


class OverlapTests(MongoApiTestCase):
    def setUp(self):
        super().setUp()
        self.customer_id = self.create_customer()
        self.type_id = self.create_type()

    def test_partial_overlap_returns_409(self):
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 201)
        response = self.book(self.customer_id, self.type_id, future_time(hour=9, minute=30))
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"]["code"], "conflict")

    def test_back_to_back_appointments_are_allowed(self):
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 201)
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=10)).status_code, 201)

    def test_concurrent_requests_for_same_slot_allow_exactly_one(self):
        payload = appointment_payload(self.customer_id, self.type_id, future_time(hour=13))
        workers = 8
        barrier = Barrier(workers)

        def attempt(_):
            client = APIClient()
            barrier.wait()
            return client.post("/api/appointments/", payload, format="json").status_code

        with ThreadPoolExecutor(max_workers=workers) as pool:
            codes = list(pool.map(attempt, range(workers)))

        self.assertEqual(codes.count(201), 1, codes)
        self.assertEqual(codes.count(409), workers - 1, codes)
