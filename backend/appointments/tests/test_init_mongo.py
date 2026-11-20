from io import StringIO

from django.core.management import call_command

from appointments.mongo import APPOINTMENT_SLOTS, get_db

from .base import MongoApiTestCase


class InitMongoTests(MongoApiTestCase):
    def test_init_is_repeatable_and_keeps_existing_documents(self):
        get_db()[APPOINTMENT_SLOTS].insert_one({"slot_at": "marker", "appointment_id": "keep"})

        call_command("init_mongo", stdout=StringIO())
        call_command("init_mongo", stdout=StringIO())

        indexes = get_db()[APPOINTMENT_SLOTS].index_information()
        self.assertTrue(indexes["uniq_slot"]["unique"])
        self.assertEqual(get_db()[APPOINTMENT_SLOTS].count_documents({"appointment_id": "keep"}), 1)
