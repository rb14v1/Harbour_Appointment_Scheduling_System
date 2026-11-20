from django.urls import path

from . import views
from .healthz import HealthzView

urlpatterns = [
    path("healthz/", HealthzView.as_view(), name="healthz"),
    path("customers/", views.CustomerListView.as_view(), name="customer-list"),
    path("customers/<str:customer_id>/", views.CustomerDetailView.as_view(), name="customer-detail"),
    path("appointment-types/", views.AppointmentTypeListView.as_view(), name="appointment-type-list"),
    path(
        "appointment-types/<str:type_id>/",
        views.AppointmentTypeDetailView.as_view(),
        name="appointment-type-detail",
    ),
    path("appointments/", views.AppointmentListView.as_view(), name="appointment-list"),
    path(
        "appointments/<str:appointment_id>/",
        views.AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
    path(
        "appointments/<str:appointment_id>/reschedule/",
        views.AppointmentRescheduleView.as_view(),
        name="appointment-reschedule",
    ),
    path(
        "appointments/<str:appointment_id>/complete/",
        views.AppointmentCompleteView.as_view(),
        name="appointment-complete",
    ),
    path(
        "appointments/<str:appointment_id>/cancel/",
        views.AppointmentCancelView.as_view(),
        name="appointment-cancel",
    ),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
]
