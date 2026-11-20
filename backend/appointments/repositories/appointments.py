from pymongo import ReturnDocument

from ..mongo import APPOINTMENTS, get_db


def _collection():
    return get_db()[APPOINTMENTS]


def insert_appointment(doc):
    _collection().insert_one(doc)
    return doc


def get_appointment(appointment_id):
    return _collection().find_one({"_id": appointment_id})


def update_appointment(appointment_id, fields, extra_filter=None):
    """Update one appointment. extra_filter makes the update conditional (optimistic check)."""
    query = {"_id": appointment_id, **(extra_filter or {})}
    return _collection().find_one_and_update(
        query,
        {"$set": fields},
        return_document=ReturnDocument.AFTER,
    )


def delete_appointment(appointment_id):
    return _collection().delete_one({"_id": appointment_id}).deleted_count == 1


def all_appointments():
    return list(_collection().find())


def find_appointments(query):
    return list(_collection().find(query).sort("start_at", 1))


def recent_appointments(limit):
    return list(_collection().find().sort("created_at", -1).limit(limit))


def count_appointments(query):
    return _collection().count_documents(query)


def dashboard_facets(today, now):
    pipeline = [
        {
            "$facet": {
                "total": [{"$count": "n"}],
                "today": [
                    {"$match": {"date": today, "status": {"$ne": "cancelled"}}},
                    {"$count": "n"},
                ],
                "upcoming": [
                    {"$match": {"status": "scheduled", "start_at": {"$gte": now}}},
                    {"$count": "n"},
                ],
                "completed": [{"$match": {"status": "completed"}}, {"$count": "n"}],
                "cancelled": [{"$match": {"status": "cancelled"}}, {"$count": "n"}],
                "by_type": [
                    {"$group": {"_id": "$type_id", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ],
            }
        }
    ]
    return next(_collection().aggregate(pipeline), {})
