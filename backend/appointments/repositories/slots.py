from ..mongo import APPOINTMENT_SLOTS, get_db


def _collection():
    return get_db()[APPOINTMENT_SLOTS]


def insert_slots(slot_docs):
    _collection().insert_many(slot_docs)


def delete_slots(appointment_id):
    _collection().delete_many({"appointment_id": appointment_id})


def delete_slots_at(appointment_id, slot_times):
    _collection().delete_many({"appointment_id": appointment_id, "slot_at": {"$in": list(slot_times)}})


def all_slots():
    return list(_collection().find())


def delete_slots_by_ids(slot_ids):
    return _collection().delete_many({"_id": {"$in": list(slot_ids)}}).deleted_count
