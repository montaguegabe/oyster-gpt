from __future__ import annotations

from decimal import Decimal

from config.fields import PublicIdField
from django.db import models
from django.db.models import F
from django.utils import timezone

MICRODOLLARS = Decimal(1_000_000)


def to_microdollars(dollars: Decimal) -> int:
    return int((dollars * MICRODOLLARS).to_integral_value())


class DailySpend(models.Model):
    """💸 Anthropic spend for one UTC day, in millionths of a dollar.

    ``microdollars`` includes reservations for requests still in flight, so the
    conditional reserve in ``reserve`` keeps the day under budget even when many
    requests arrive at once.
    """

    public_id = PublicIdField()
    day = models.DateField(unique=True)
    microdollars = models.BigIntegerField(default=0)
    requests = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("-day",)

    def __str__(self) -> str:
        return f"{self.day}: ${Decimal(self.microdollars) / MICRODOLLARS:.4f} ({self.requests} requests)"

    @classmethod
    def reserve(cls, amount: Decimal, budget: Decimal):
        """Reserve ``amount`` against today's ``budget``. Returns the day, or None when over budget."""
        day = timezone.now().date()
        cls.objects.get_or_create(day=day)
        reserved = cls.objects.filter(
            day=day, microdollars__lte=to_microdollars(budget) - to_microdollars(amount)
        ).update(
            microdollars=F("microdollars") + to_microdollars(amount),
            requests=F("requests") + 1,
        )
        return day if reserved else None

    @classmethod
    def settle(cls, day, reserved: Decimal, actual: Decimal) -> None:
        """Replace a reservation with the request's actual cost (zero when the call failed)."""
        cls.objects.filter(day=day).update(
            microdollars=F("microdollars")
            + to_microdollars(actual)
            - to_microdollars(reserved)
        )
