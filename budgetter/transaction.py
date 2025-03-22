import datetime
from pydantic import BaseModel


class Transaction(BaseModel):
    amount: float
    description: str
    when: datetime.datetime
    from_: str
    to_: str

    def flip(self):
        return Transaction(
            amount=-self.amount,
            description=self.description,
            when=self.when,
            from_=self.to_,
            to_=self.from_,
        )
