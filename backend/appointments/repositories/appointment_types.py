from pymongo import ReturnDocument

from ..mongo import APPOINTMENT_TYPES, get_db


def _collection():
    return get_db()[APPOINTMENT_TYPES]


def list_types():
    return list(_collection().find().sort("name", 1))


def get_type(type_id):
    return _collection().find_one({"_id": type_id})


def get_types_by_ids(type_ids):
    return list(_collection().find({"_id": {"$in": type_ids}}))


def insert_type(doc):
    _collection().insert_one(doc)
    return doc


def update_type(type_id, fields):
    return _collection().find_one_and_update(
        {"_id": type_id},
        {"$set": fields},
        return_document=ReturnDocument.AFTER,
    )


def delete_type(type_id):
    return _collection().delete_one({"_id": type_id}).deleted_count == 1
