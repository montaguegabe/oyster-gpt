from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import anthropic
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .models import DailySpend
from .oyster import MODEL, SILENCE, ask_claude
from .serializers import ChatSerializer

PAGE = Path(__file__).parent / "page" / "index.html"

client = anthropic.Anthropic(
    api_key=settings.OYSTERGPT_ANTHROPIC_API_KEY, max_retries=1
)


class OysterUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "ANTHROPIC_API_KEY is not configured."


def page(request):
    return HttpResponse(PAGE.read_bytes(), content_type="text/html; charset=utf-8")


class ChatThrottle(AnonRateThrottle):
    scope = "oystergpt_chat"
    rate = "30/hour"


class ChatView(APIView):
    """Public, so every message reserves its worst-case cost against the daily budget first."""

    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ChatThrottle,)

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not settings.OYSTERGPT_ANTHROPIC_API_KEY:
            raise OysterUnavailable
        reserve = Decimal(settings.OYSTERGPT_REQUEST_RESERVE_USD)
        day = DailySpend.reserve(reserve, Decimal(settings.OYSTERGPT_DAILY_BUDGET_USD))
        if day is None:
            return Response(
                {"reply": SILENCE, "asleep": True, "searches": [], "model": MODEL}
            )

        cost = Decimal(0)
        try:
            result = ask_claude(client, serializer.validated_data["messages"])
            cost = result.cost
        finally:
            DailySpend.settle(day, reserve, cost)
        return Response(
            {
                "reply": result.reply,
                "asleep": False,
                "searches": result.searches,
                "model": MODEL,
            }
        )
