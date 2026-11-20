from ..mongo import APPOINTMENT_SLOTS, get_db


def _collection():
    return get_db()[APPOINTMENT_SLOTS]


def insert_slots(slot_docs, session=None):
    _collection().insert_many(slot_docs, session=session)


def delete_slots(appointment_id, session=None):
    _collection().delete_many({"appointment_id": appointment_id}, session=session)
