from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentFilterSerializer,
    AppointmentTypeInputSerializer,
    AppointmentUpdateSerializer,
    CustomerInputSerializer,
    RescheduleSerializer,
)


def _validated(serializer_class, data, partial=False):
    serializer = serializer_class(data=data, partial=partial)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class CustomerListView(APIView):
    def get(self, request):
        search = request.query_params.get("search", "").strip()
        return Response(services.list_customers(search))

    def post(self, request):
        data = _validated(CustomerInputSerializer, request.data)
        return Response(services.create_customer(data), status=status.HTTP_201_CREATED)


class CustomerDetailView(APIView):
    def get(self, request, customer_id):
        return Response(services.get_customer(customer_id))

    def patch(self, request, customer_id):
        data = _validated(CustomerInputSerializer, request.data, partial=True)
        return Response(services.update_customer(customer_id, data))

    def delete(self, request, customer_id):
        services.delete_customer(customer_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AppointmentTypeListView(APIView):
    def get(self, request):
        return Response(services.list_types())

    def post(self, request):
        data = _validated(AppointmentTypeInputSerializer, request.data)
        return Response(services.create_type(data), status=status.HTTP_201_CREATED)


class AppointmentTypeDetailView(APIView):
    def get(self, request, type_id):
        return Response(services.get_type(type_id))

    def patch(self, request, type_id):
        data = _validated(AppointmentTypeInputSerializer, request.data, partial=True)
        return Response(services.update_type(type_id, data))

    def delete(self, request, type_id):
        services.delete_type(type_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AppointmentListView(APIView):
    def get(self, request):
        filters = _validated(AppointmentFilterSerializer, request.query_params)
        return Response(services.list_appointments(filters))

    def post(self, request):
        data = _validated(AppointmentCreateSerializer, request.data)
        appointment = services.create_appointment(data)
        return Response(services.present_appointment(appointment), status=status.HTTP_201_CREATED)


class AppointmentDetailView(APIView):
    def get(self, request, appointment_id):
        appointment = services.get_appointment(appointment_id)
        return Response(services.present_appointment(appointment))

    def patch(self, request, appointment_id):
        data = _validated(AppointmentUpdateSerializer, request.data, partial=True)
        appointment = services.update_appointment(appointment_id, data)
        return Response(services.present_appointment(appointment))


class AppointmentRescheduleView(APIView):
    def post(self, request, appointment_id):
        data = _validated(RescheduleSerializer, request.data)
        appointment = services.reschedule_appointment(appointment_id, data)
        return Response(services.present_appointment(appointment))


class AppointmentCompleteView(APIView):
    def post(self, request, appointment_id):
        appointment = services.complete_appointment(appointment_id)
        return Response(services.present_appointment(appointment))


class AppointmentCancelView(APIView):
    def post(self, request, appointment_id):
        appointment = services.cancel_appointment(appointment_id)
        return Response(services.present_appointment(appointment))


class DashboardView(APIView):
    def get(self, request):
        return Response(services.get_dashboard())
