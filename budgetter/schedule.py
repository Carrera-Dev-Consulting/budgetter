import datetime
from functools import cached_property
import re
from typing import Iterable
from dateutil import relativedelta
from pydantic import BaseModel

from budgetter.account import Account
from budgetter.transaction import Transaction
from budgetter.debt import InterestIntervals, calc_interest

KNOWN_PATTERNS = {
    "\\d+ weeks": lambda weeks: relativedelta.relativedelta(weeks=weeks),
    "\\d+ months": lambda months: relativedelta.relativedelta(months=months),
    "\\d+ years": lambda years: relativedelta.relativedelta(years=years),
    "monthly": lambda _: relativedelta.relativedelta(months=1),
    "yearly": lambda _: relativedelta.relativedelta(years=1),
    "annually": lambda _: relativedelta.relativedelta(years=1),
    "bi-weekly": lambda _: relativedelta.relativedelta(weeks=2),
}


def parse_schedule_repeat(schedule: str):
    for pattern in KNOWN_PATTERNS:
        match = re.match(pattern, schedule)
        if match:
            value = match.group(0)
            repeat = KNOWN_PATTERNS[pattern](int(value) if value.isnumeric() else value)
            return repeat
    raise ValueError(f"Unknown schedule: {schedule}")


class BaseSchedule(BaseModel):
    name: str
    to: Account
    amount: float
    started: datetime.date
    repeat_str: str

    @cached_property
    def repeat(self) -> relativedelta.relativedelta:
        return parse_schedule_repeat(self.repeat_str)


class PaymentSchedule(BaseSchedule):
    def calculate_future_payments(
        self, end: datetime.datetime
    ) -> Iterable[Transaction]:
        current = self.started
        current_amount = self.amount
        end = end.date()
        while current < end:
            yield Transaction(
                amount=current_amount,
                description=f"Scheduled Payment of {self.name} for {self.to.name}",
                when=current,
                from_=self.to.name,
                to_=self.to.name,
            )
            current += self.repeat


class InterestSchedule(BaseSchedule):
    rate: float
    frequency: InterestIntervals

    def calculate_future_payments(
        self, end: datetime.datetime
    ) -> Iterable[Transaction]:
        current = self.started
        balance = self.to.balance
        end = end.date()
        while current < end:
            amount = calc_interest(balance, self.rate, self.frequency)
            yield Transaction(
                amount=amount,
                description=f"Scheduled Payment of {self.name} for {self.name}",
                when=current,
                from_=self.from_.name,
                to_=self.to.name,
            )
            balance += amount
            current += self.repeat
            if isinstance(current, datetime.datetime):
                current = current.date()


class TransferSchedule(BaseSchedule):
    from_: Account

    def calculate_future_payments(
        self, end: datetime.datetime
    ) -> Iterable[Transaction]:
        current = self.started
        end = end.date()
        while current < end:
            yield Transaction(
                amount=self.amount,
                from_=self.from_.name,
                to_=self.to.name,
                description=f"Transfering from {self.from_.name} to {self.to.name}",
                when=current,
            )
            current += self.repeat
