import re

from pymongo import ReturnDocument

from ..mongo import CUSTOMERS, get_db


def _collection():
    return get_db()[CUSTOMERS]


def list_customers(search=""):
    query = {}
    if search:
        pattern = {"$regex": re.escape(search), "$options": "i"}
        query = {"$or": [{"full_name": pattern}, {"email": pattern}, {"phone": pattern}]}
    return list(_collection().find(query).sort("full_name", 1))


def get_customer(customer_id):
    return _collection().find_one({"_id": customer_id})


def get_customers_by_ids(customer_ids):
    return list(_collection().find({"_id": {"$in": customer_ids}}))


def insert_customer(doc):
    _collection().insert_one(doc)
    return doc


def update_customer(customer_id, fields):
    return _collection().find_one_and_update(
        {"_id": customer_id},
        {"$set": fields},
        return_document=ReturnDocument.AFTER,
    )


def delete_customer(customer_id):
    return _collection().delete_one({"_id": customer_id}).deleted_count == 1
