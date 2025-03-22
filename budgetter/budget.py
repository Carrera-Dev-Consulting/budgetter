from collections import defaultdict
import datetime
from pydantic import BaseModel, field_validator

from budgetter.account import Account
from budgetter.schedule import TransferSchedule, PaymentSchedule


class Budget(BaseModel):
    accounts: dict[str, Account] = {}
    payment_schedules: dict[str, list[PaymentSchedule]] = {}
    transfer_schedules: dict[str, list[TransferSchedule]] = {}

    def add_account(self, account: Account):
        self.accounts[account.name] = account

    def add_payment_schedule(
        self,
        schedule_name: str,
        account: Account,
        repeat_str: str,
        amount: float,
        start_date: str | datetime.date,
    ):
        name = account.name
        if name not in self.payment_schedules:
            self.payment_schedules[name] = []
        self.payment_schedules[name].append(
            PaymentSchedule(
                name=schedule_name,
                to=account,
                amount=amount,
                repeat_str=repeat_str,
                started=start_date,
            )
        )

    def add_transfer_schedule(
        self,
        from_: Account,
        to: Account,
        repeat_str: str,
        schedule_name: str,
        amount: float,
        start_date: str,
    ):
        name = to.name
        if name not in self.transfer_schedules:
            self.transfer_schedules[name] = []
        self.transfer_schedules[name].append(
            TransferSchedule(
                name=schedule_name,
                amount=amount,
                from_=from_,
                to=to,
                repeat_str=repeat_str,
                started=start_date,
            )
        )

    def forecast_account(
        self,
        account_name: str,
        end: datetime.datetime,
    ):
        account = self.accounts[account_name]
        forecasted = account
        for payment_schedule in self.payment_schedules[account_name]:
            forecasted = forecasted.forecast(
                possible_transactions=payment_schedule.calculate_future_payments(end)
            )
        for transfer_schedule in self.transfer_schedules[account_name]:
            forecasted = forecasted.forecast(
                possible_transactions=transfer_schedule.calculate_future_payments(end)
            )
        return forecasted
