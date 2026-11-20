from datetime import timezone

from bson import ObjectId
from pymongo.errors import BulkWriteError, DuplicateKeyError

from .exceptions import AppError, ConflictError, NotFoundError
from .repositories import appointment_types as types_repo
from .repositories import appointments as appointments_repo
from .repositories import customers as customers_repo
from .repositories import slots as slots_repo
from .serializers import serialize_appointment, serialize_appointment_type, serialize_customer
from .timeutils import is_on_grid, local_date_string, now_utc, slot_starts

SCHEDULED = "scheduled"
COMPLETED = "completed"
CANCELLED = "cancelled"

RECENT_LIMIT = 10
DUPLICATE_EMAIL = "A customer with this email already exists."
DUPLICATE_TYPE = "An appointment type with this name already exists."
OVERLAP = "The selected time overlaps another active appointment."
CHANGED_ELSEWHERE = "The appointment was changed by another request. Refresh and try again."


# Id and reference helpers

def _path_id(value, label):
    if not ObjectId.is_valid(value):
        raise NotFoundError(f"{label} not found.")
    return ObjectId(value)


def _body_id(value, field):
    if not ObjectId.is_valid(value):
        raise AppError(f"{field} must be a valid id.")
    return ObjectId(value)


def _require_customer(value):
    doc = customers_repo.get_customer(_body_id(value, "customer_id"))
    if doc is None:
        raise AppError("Selected customer does not exist.")
    return doc


def _require_active_type(value):
    doc = types_repo.get_type(_body_id(value, "appointment_type_id"))
    if doc is None:
        raise AppError("Selected appointment type does not exist.")
    if not doc["is_active"]:
        raise AppError("Selected appointment type is inactive.")
    return doc


# Time rules

def _validated_window(start_at, end_at):
    start = start_at.astimezone(timezone.utc)
    end = end_at.astimezone(timezone.utc)
    if not (is_on_grid(start) and is_on_grid(end)):
        raise AppError("Start and end times must fall on 15-minute intervals.")
    if end <= start:
        raise AppError("End time must be later than start time.")
    if start < now_utc():
        raise AppError("Appointments cannot be scheduled in the past.")
    return start, end


def _slot_documents(appointment_id, start, end):
    return [{"slot_at": slot, "appointment_id": appointment_id} for slot in slot_starts(start, end)]


def _claim_slots(appointment_id, slot_docs):
    """Insert slot blocks. The unique slot index rejects overlaps; on conflict, remove what was inserted here."""
    if not slot_docs:
        return
    try:
        slots_repo.insert_slots(slot_docs)
    except (BulkWriteError, DuplicateKeyError) as exc:
        slots_repo.delete_slots_at(appointment_id, [doc["slot_at"] for doc in slot_docs])
        raise ConflictError(OVERLAP) from exc


# Customers

def list_customers(search=""):
    return [serialize_customer(doc) for doc in customers_repo.list_customers(search)]


def get_customer(customer_id):
    doc = customers_repo.get_customer(_path_id(customer_id, "Customer"))
    if doc is None:
        raise NotFoundError("Customer not found.")
    return serialize_customer(doc)


def _customer_fields(data):
    return {key: data[key] for key in ("full_name", "email", "phone", "address") if key in data}


def create_customer(data):
    now = now_utc()
    doc = {"_id": ObjectId(), **_customer_fields(data), "created_at": now, "updated_at": now}
    try:
        customers_repo.insert_customer(doc)
    except DuplicateKeyError as exc:
        raise ConflictError(DUPLICATE_EMAIL) from exc
    return serialize_customer(doc)


def update_customer(customer_id, data):
    fields = {**_customer_fields(data), "updated_at": now_utc()}
    try:
        doc = customers_repo.update_customer(_path_id(customer_id, "Customer"), fields)
    except DuplicateKeyError as exc:
        raise ConflictError(DUPLICATE_EMAIL) from exc
    if doc is None:
        raise NotFoundError("Customer not found.")
    return serialize_customer(doc)


def delete_customer(customer_id):
    oid = _path_id(customer_id, "Customer")
    if customers_repo.get_customer(oid) is None:
        raise NotFoundError("Customer not found.")
    if appointments_repo.count_appointments({"customer_id": oid}) > 0:
        raise ConflictError("Customer has appointments and cannot be deleted.")
    customers_repo.delete_customer(oid)


# Appointment types

def list_types():
    return [serialize_appointment_type(doc) for doc in types_repo.list_types()]


def get_type(type_id):
    doc = types_repo.get_type(_path_id(type_id, "Appointment type"))
    if doc is None:
        raise NotFoundError("Appointment type not found.")
    return serialize_appointment_type(doc)


def _type_fields(data):
    return {
        key: data[key]
        for key in ("name", "description", "duration_minutes", "is_active")
        if key in data
    }


def create_type(data):
    now = now_utc()
    doc = {"_id": ObjectId(), **_type_fields(data), "created_at": now, "updated_at": now}
    try:
        types_repo.insert_type(doc)
    except DuplicateKeyError as exc:
        raise ConflictError(DUPLICATE_TYPE) from exc
    return serialize_appointment_type(doc)


def update_type(type_id, data):
    fields = {**_type_fields(data), "updated_at": now_utc()}
    try:
        doc = types_repo.update_type(_path_id(type_id, "Appointment type"), fields)
    except DuplicateKeyError as exc:
        raise ConflictError(DUPLICATE_TYPE) from exc
    if doc is None:
        raise NotFoundError("Appointment type not found.")
    return serialize_appointment_type(doc)


def delete_type(type_id):
    oid = _path_id(type_id, "Appointment type")
    if types_repo.get_type(oid) is None:
        raise NotFoundError("Appointment type not found.")
    if appointments_repo.count_appointments({"type_id": oid}) > 0:
        raise ConflictError("Appointment type is used by appointments and cannot be deleted.")
    types_repo.delete_type(oid)


# Appointments

def present_appointments(docs):
    customer_ids = list({doc["customer_id"] for doc in docs})
    type_ids = list({doc["type_id"] for doc in docs})
    customer_names = {c["_id"]: c["full_name"] for c in customers_repo.get_customers_by_ids(customer_ids)}
    type_names = {t["_id"]: t["name"] for t in types_repo.get_types_by_ids(type_ids)}
    return [
        serialize_appointment(
            doc,
            customer_names.get(doc["customer_id"], "Unknown customer"),
            type_names.get(doc["type_id"], "Unknown type"),
        )
        for doc in docs
    ]


def present_appointment(doc):
    return present_appointments([doc])[0]


def list_appointments(filters):
    query = {}
    date_range = {}
    if "date_from" in filters:
        date_range["$gte"] = filters["date_from"].isoformat()
    if "date_to" in filters:
        date_range["$lte"] = filters["date_to"].isoformat()
    if date_range:
        query["date"] = date_range
    if "customer_id" in filters:
        query["customer_id"] = _body_id(filters["customer_id"], "customer_id")
    if "type_id" in filters:
        query["type_id"] = _body_id(filters["type_id"], "type_id")
    if "status" in filters:
        query["status"] = filters["status"]
    return present_appointments(appointments_repo.find_appointments(query))


def get_appointment(appointment_id):
    doc = appointments_repo.get_appointment(_path_id(appointment_id, "Appointment"))
    if doc is None:
        raise NotFoundError("Appointment not found.")
    return doc


def create_appointment(data):
    customer = _require_customer(data["customer_id"])
    appointment_type = _require_active_type(data["appointment_type_id"])
    start, end = _validated_window(data["start_at"], data["end_at"])
    now = now_utc()
    appointment = {
        "_id": ObjectId(),
        "customer_id": customer["_id"],
        "type_id": appointment_type["_id"],
        "start_at": start,
        "end_at": end,
        "date": local_date_string(start),
        "description": data["description"],
        "status": SCHEDULED,
        "created_at": now,
        "updated_at": now,
    }

    # Save the appointment first, then its slots. If the slots are refused or fail,
    # remove the appointment so no booking is left without its time reserved.
    appointments_repo.insert_appointment(appointment)
    try:
        _claim_slots(appointment["_id"], _slot_documents(appointment["_id"], start, end))
    except Exception:
        appointments_repo.delete_appointment(appointment["_id"])
        raise
    return appointment


def update_appointment(appointment_id, data):
    oid = _path_id(appointment_id, "Appointment")
    current = get_appointment(appointment_id)

    if "customer_id" in data or "appointment_type_id" in data:
        if current["status"] != SCHEDULED:
            raise ConflictError("Only scheduled appointments can change customer or appointment type.")

    fields = {}
    if "description" in data:
        fields["description"] = data["description"]
    if "customer_id" in data:
        fields["customer_id"] = _require_customer(data["customer_id"])["_id"]
    if "appointment_type_id" in data:
        fields["type_id"] = _require_active_type(data["appointment_type_id"])["_id"]
    if not fields:
        return current

    fields["updated_at"] = now_utc()
    updated = appointments_repo.update_appointment(oid, fields)
    if updated is None:
        raise NotFoundError("Appointment not found.")
    return updated


def reschedule_appointment(appointment_id, data):
    oid = _path_id(appointment_id, "Appointment")
    start, end = _validated_window(data["start_at"], data["end_at"])

    current = appointments_repo.get_appointment(oid)
    if current is None:
        raise NotFoundError("Appointment not found.")
    if current["status"] != SCHEDULED:
        raise ConflictError(f"{current['status'].capitalize()} appointments cannot be rescheduled.")

    # Claim only the new blocks. Blocks the appointment already holds are kept,
    # so the old booking is never released before its replacement is secured.
    old_times = set(slot_starts(current["start_at"], current["end_at"]))
    new_docs = _slot_documents(oid, start, end)
    new_times = {doc["slot_at"] for doc in new_docs}
    to_claim = [doc for doc in new_docs if doc["slot_at"] not in old_times]
    _claim_slots(oid, to_claim)

    updated = appointments_repo.update_appointment(
        oid,
        {"start_at": start, "end_at": end, "date": local_date_string(start), "updated_at": now_utc()},
        extra_filter={"status": SCHEDULED, "start_at": current["start_at"], "end_at": current["end_at"]},
    )
    if updated is None:
        slots_repo.delete_slots_at(oid, [doc["slot_at"] for doc in to_claim])
        raise ConflictError(CHANGED_ELSEWHERE)

    released = sorted(old_times - new_times)
    if released:
        slots_repo.delete_slots_at(oid, released)
    return updated


def _change_status(appointment_id, new_status):
    oid = _path_id(appointment_id, "Appointment")
    updated = appointments_repo.update_appointment(
        oid,
        {"status": new_status, "updated_at": now_utc()},
        extra_filter={"status": SCHEDULED},
    )
    if updated is None:
        if appointments_repo.get_appointment(oid) is None:
            raise NotFoundError("Appointment not found.")
        raise ConflictError(f"Only scheduled appointments can be {new_status}.")
    if new_status == CANCELLED:
        slots_repo.delete_slots(oid)
    return updated


def complete_appointment(appointment_id):
    return _change_status(appointment_id, COMPLETED)


def cancel_appointment(appointment_id):
    return _change_status(appointment_id, CANCELLED)


# Repair

def repair_slots():
    """Remove slot blocks that no live appointment owns. Report active appointments with missing blocks."""
    appointments = {doc["_id"]: doc for doc in appointments_repo.all_appointments()}
    stale_ids = []
    held = set()
    for slot in slots_repo.all_slots():
        owner = appointments.get(slot["appointment_id"])
        in_range = owner is not None and owner["start_at"] <= slot["slot_at"] < owner["end_at"]
        if owner is None or owner["status"] == CANCELLED or not in_range:
            stale_ids.append(slot["_id"])
        else:
            held.add((slot["appointment_id"], slot["slot_at"]))

    removed = slots_repo.delete_slots_by_ids(stale_ids) if stale_ids else 0
    missing = sum(
        1
        for owner in appointments.values()
        if owner["status"] != CANCELLED
        for slot_at in slot_starts(owner["start_at"], owner["end_at"])
        if (owner["_id"], slot_at) not in held
    )
    return {"removed": removed, "missing": missing}


# Dashboard

def _facet_count(facets, key):
    rows = facets.get(key) or []
    return rows[0]["n"] if rows else 0


def get_dashboard():
    now = now_utc()
    facets = appointments_repo.dashboard_facets(today=local_date_string(now), now=now)
    type_names = {t["_id"]: t["name"] for t in types_repo.list_types()}
    return {
        "total": _facet_count(facets, "total"),
        "today": _facet_count(facets, "today"),
        "upcoming": _facet_count(facets, "upcoming"),
        "completed": _facet_count(facets, "completed"),
        "cancelled": _facet_count(facets, "cancelled"),
        "recent": present_appointments(appointments_repo.recent_appointments(RECENT_LIMIT)),
        "by_type": [
            {
                "type_id": str(row["_id"]),
                "type_name": type_names.get(row["_id"], "Unknown type"),
                "count": row["count"],
            }
            for row in facets.get("by_type", [])
        ],
    }
