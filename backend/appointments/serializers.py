from datetime import timezone

from rest_framework import serializers

from .timeutils import SLOT_MINUTES

STATUS_CHOICES = ("scheduled", "completed", "cancelled")


# Input serializers

class CustomerInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120)
    email = serializers.EmailField(max_length=254)
    phone = serializers.CharField(max_length=30)
    address = serializers.CharField(max_length=300, allow_blank=True, required=False, default="")

    def validate_email(self, value):
        return value.lower()


class AppointmentTypeInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=80)
    description = serializers.CharField(max_length=500, allow_blank=True, required=False, default="")
    duration_minutes = serializers.IntegerField(min_value=SLOT_MINUTES, max_value=480)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_duration_minutes(self, value):
        if value % SLOT_MINUTES:
            raise serializers.ValidationError(f"Duration must be a multiple of {SLOT_MINUTES} minutes.")
        return value


class AppointmentCreateSerializer(serializers.Serializer):
    customer_id = serializers.CharField(max_length=24)
    appointment_type_id = serializers.CharField(max_length=24)
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    description = serializers.CharField(max_length=1000, allow_blank=True, required=False, default="")


class AppointmentUpdateSerializer(serializers.Serializer):
    customer_id = serializers.CharField(max_length=24, required=False)
    appointment_type_id = serializers.CharField(max_length=24, required=False)
    description = serializers.CharField(max_length=1000, allow_blank=True, required=False)

    def validate(self, attrs):
        if {"start_at", "end_at"} & set(self.initial_data):
            raise serializers.ValidationError(
                "Use the reschedule endpoint to change appointment times."
            )
        return attrs


class RescheduleSerializer(serializers.Serializer):
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()


class AppointmentFilterSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    customer_id = serializers.CharField(max_length=24, required=False)
    type_id = serializers.CharField(max_length=24, required=False)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, required=False)


# Output helpers

def _iso(value):
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def serialize_customer(doc):
    return {
        "id": str(doc["_id"]),
        "full_name": doc["full_name"],
        "email": doc["email"],
        "phone": doc["phone"],
        "address": doc["address"],
        "created_at": _iso(doc["created_at"]),
        "updated_at": _iso(doc["updated_at"]),
    }


def serialize_appointment_type(doc):
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "description": doc["description"],
        "duration_minutes": doc["duration_minutes"],
        "is_active": doc["is_active"],
        "created_at": _iso(doc["created_at"]),
        "updated_at": _iso(doc["updated_at"]),
    }


def serialize_appointment(doc, customer_name, type_name):
    return {
        "id": str(doc["_id"]),
        "customer_id": str(doc["customer_id"]),
        "customer_name": customer_name,
        "appointment_type_id": str(doc["type_id"]),
        "appointment_type_name": type_name,
        "start_at": _iso(doc["start_at"]),
        "end_at": _iso(doc["end_at"]),
        "date": doc["date"],
        "description": doc["description"],
        "status": doc["status"],
        "created_at": _iso(doc["created_at"]),
        "updated_at": _iso(doc["updated_at"]),
    }
