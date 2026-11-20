from io import StringIO

from django.core.management import call_command
from bson import ObjectId

from appointments import services
from appointments.mongo import APPOINTMENT_SLOTS, get_db

from .base import MongoApiTestCase, future_time


class RepairTests(MongoApiTestCase):
    def setUp(self):
        super().setUp()
        self.customer_id = self.create_customer()
        self.type_id = self.create_type()

    def test_repair_removes_stale_slots_and_keeps_live_ones(self):
        self.book(self.customer_id, self.type_id, future_time(hour=9))
        get_db()[APPOINTMENT_SLOTS].insert_one({"slot_at": future_time(hour=15), "appointment_id": ObjectId()})

        result = services.repair_slots()

        self.assertEqual(result["removed"], 1)
        self.assertEqual(result["missing"], 0)
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 409)

    def test_cancelled_appointment_slots_are_removed_by_repair(self):
        booked = self.book(self.customer_id, self.type_id, future_time(hour=9)).json()
        get_db()["appointments"].update_one({"_id": ObjectId(booked["id"])}, {"$set": {"status": "cancelled"}})

        result = services.repair_slots()

        self.assertEqual(result["removed"], 4)
        self.assertEqual(self.book(self.customer_id, self.type_id, future_time(hour=9)).status_code, 201)

    def test_repair_command_runs(self):
        out = StringIO()
        call_command("repair_mongo", stdout=out)
        self.assertIn("Removed 0 stale slot(s).", out.getvalue())
