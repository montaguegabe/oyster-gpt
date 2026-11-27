from decimal import Decimal
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from oystergpt_api.oystergpt.models import DailySpend, to_microdollars
from oystergpt_api.oystergpt.oyster import OysterReply

pytestmark = pytest.mark.django_db

ASK = "oystergpt_api.oystergpt.views.ask_claude"
HELLO = {"messages": [{"role": "user", "content": "hello oyster"}]}


@pytest.fixture(autouse=True)
def oyster_settings(settings):
    settings.OYSTERGPT_ANTHROPIC_API_KEY = "test-key"
    settings.OYSTERGPT_DAILY_BUDGET_USD = "2.00"
    settings.OYSTERGPT_REQUEST_RESERVE_USD = "0.30"
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
    }


def today_spend():
    return DailySpend.objects.get().microdollars


def chat(payload=HELLO):
    return APIClient().post(reverse("oystergpt-chat"), payload, format="json")


def test_page_serves_the_chat():
    response = APIClient().get(reverse("oystergpt-page"))
    assert response.status_code == 200
    assert b"OysterGPT" in response.content


def test_chat_records_the_actual_cost():
    reply = OysterReply(
        reply="blub", cost=Decimal("0.0961"), searches=["oyster prices boston"]
    )
    with patch(ASK, return_value=reply) as ask:
        response = chat()
    assert response.status_code == 200
    assert response.json() == {
        "reply": "blub",
        "asleep": False,
        "searches": ["oyster prices boston"],
        "model": "claude-opus-5-5",
    }
    assert ask.call_args.args[1] == HELLO["messages"]
    assert today_spend() == to_microdollars(Decimal("0.0961"))


def test_chat_sleeps_without_calling_claude_once_the_budget_is_spent():
    DailySpend.objects.create(day=timezone.now().date(), microdollars=1_800_001)
    with patch(ASK) as ask:
        response = chat()
    assert response.json()["asleep"] is True
    ask.assert_not_called()
    assert today_spend() == 1_800_001


def test_reservations_never_exceed_the_budget():
    granted = [DailySpend.reserve(Decimal("0.30"), Decimal("2.00")) for _ in range(10)]
    assert sum(day is not None for day in granted) == 6
    assert today_spend() == to_microdollars(Decimal("1.80"))


def test_failed_call_refunds_its_reservation():
    with (
        patch(ASK, side_effect=RuntimeError("tide is out")),
        pytest.raises(RuntimeError),
    ):
        chat()
    assert today_spend() == 0


def test_conversation_must_end_with_a_human_message():
    payload = {
        "messages": [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "..."},
        ]
    }
    with patch(ASK) as ask:
        response = chat(payload)
    assert response.status_code == 400
    ask.assert_not_called()


def test_missing_key_is_reported(settings):
    settings.OYSTERGPT_ANTHROPIC_API_KEY = ""
    with patch(ASK) as ask:
        response = chat()
    assert response.status_code == 503
    ask.assert_not_called()
