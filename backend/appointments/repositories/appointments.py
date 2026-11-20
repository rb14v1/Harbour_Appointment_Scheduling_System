from pymongo import ReturnDocument

from ..mongo import APPOINTMENTS, get_db


def _collection():
    return get_db()[APPOINTMENTS]


def insert_appointment(doc, session=None):
    _collection().insert_one(doc, session=session)
    return doc


def get_appointment(appointment_id, session=None):
    return _collection().find_one({"_id": appointment_id}, session=session)


def update_appointment(appointment_id, fields, session=None):
    return _collection().find_one_and_update(
        {"_id": appointment_id},
        {"$set": fields},
        return_document=ReturnDocument.AFTER,
        session=session,
    )


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
