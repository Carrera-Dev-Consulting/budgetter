import datetime
from typing import Iterable
from pydantic import BaseModel

from budgetter.transaction import Transaction


class Account(BaseModel):
    transactions: list[Transaction] = []
    name: str

    @property
    def balance(self):
        return sum(t.amount for t in self.transactions)

    @property
    def sorted_transactions(self):
        return sorted(self.transactions, key=lambda t: t.when)

    def balance_on_day(self, day: datetime.date):
        return sum(t.amount for t in self.transactions if t.when.date() <= day)

    def transfer_to(
        self,
        to_: "Account",
        amount: float,
        description: str = "Transfering money from one account to another",
    ):
        when = when or datetime.datetime.now(datetime.timezone.utc)
        transaction = Transaction(
            amount=amount,
            from_=self.name,
            to_=to_.name,
            description=description,
            when=when,
        )
        self.transactions.append(transaction.flip())
        to_.transactions.append(transaction)

    def transfer_from(
        self,
        from_: "Account",
        amount: float,
        description: str = "Transfering money from one account to another",
        when: datetime = None,
    ):
        when = when or datetime.datetime.now(datetime.timezone.utc)
        transaction = Transaction(
            amount=amount,
            from_=from_.name,
            to_=self.name,
            description=description,
            when=when,
        )
        self.transactions.append(transaction)
        from_.transactions.append(transaction.flip())

    def submit_transaction(
        self,
        source: str,
        amount: float,
        description: str = "",
        when: datetime = None,
    ):
        when = when or datetime.datetime.now()
        self.transactions.append(
            Transaction(
                amount=amount,
                from_=source,
                to_=self.name,
                description=description,
                when=when,
            )
        )

    def forecast(self, possible_transactions: Iterable[Transaction]) -> "Account":
        return Account(
            name=self.name, transactions=[*possible_transactions, *self.transactions]
        )
