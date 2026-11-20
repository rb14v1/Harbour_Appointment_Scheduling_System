from pymongo import ASCENDING

VERSION = "0001_initial_schema"
DESCRIPTION = "Create indexes for customers, appointment types, appointments and booking slots."


def up(db):
    db["customers"].create_index([("email", ASCENDING)], unique=True, name="uniq_email")
    db["customers"].create_index([("full_name", ASCENDING)], name="full_name_idx")
    db["customers"].create_index([("phone", ASCENDING)], name="phone_idx")

    db["appointment_types"].create_index([("name", ASCENDING)], unique=True, name="uniq_name")

    db["appointments"].create_index([("status", ASCENDING), ("start_at", ASCENDING)], name="status_start")
    db["appointments"].create_index([("customer_id", ASCENDING), ("start_at", ASCENDING)], name="customer_start")
    db["appointments"].create_index([("type_id", ASCENDING)], name="type_idx")
    db["appointments"].create_index([("date", ASCENDING)], name="local_date_idx")

    db["appointment_slots"].create_index([("slot_at", ASCENDING)], unique=True, name="uniq_slot")
    db["appointment_slots"].create_index([("appointment_id", ASCENDING)], name="appointment_idx")
