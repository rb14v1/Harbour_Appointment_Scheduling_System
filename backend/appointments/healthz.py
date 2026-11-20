from pymongo.errors import PyMongoError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .mongo import get_client


class HealthzView(APIView):
    """Reports whether the API can reach MongoDB. Used by people and monitoring tools to check the app is up."""

    def get(self, request):
        try:
            get_client().admin.command("ping")
        except PyMongoError:
            return Response(
                {"status": "error", "database": "unreachable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({"status": "ok", "database": "ok"})
