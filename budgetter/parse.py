import csv
import datetime
from pydantic import AliasChoices, BaseModel, Field, field_validator
import re


def parse_currency_value(text, pattern):
    match = re.search(pattern, text)
    if match:
        return match.group(2)
    else:
        return None


text = "$1,234.56"
pattern = r"(\$|\€|\£)(\d{1,3}(?:,\d{3})*(?:\.\d+)?)"


def parse_currency(text, pattern):
    return float(parse_currency_value(text, pattern).replace(",", ""))


class Expense(BaseModel):
    name: str = Field(alias=AliasChoices("name", "Name"))
    monthly: float = Field(alias=AliasChoices("monthly", "Monthly"))
    due_date: datetime.date = Field(alias=AliasChoices("due_date", "Due Date"))
    expense_type: str = Field(alias=AliasChoices("expense_type", "Expense Type"))

    @field_validator("monthly", mode="before")
    def validate_monthly(cls, v):
        return parse_currency(v, pattern)

    @field_validator("due_date", mode="before")
    def validate_due_date(cls, v):
        return datetime.datetime.strptime(v, "%m/%d/%Y").date()


class Income(BaseModel):
    name: str = Field(alias=AliasChoices("name", "Name"))
    amount: float = Field(alias=AliasChoices("amount", "Amount"))
    pay_date: datetime.date = Field(alias=AliasChoices("pay_date", "Pay Date"))
    income_type: str = Field(alias=AliasChoices("income_type", "Income type"))

    @field_validator("amount", mode="before")
    def validate_amount(cls, v):
        return parse_currency(v, pattern)

    @field_validator("pay_date", mode="before")
    def validate_due_date(cls, v):
        return datetime.datetime.strptime(v, "%m/%d/%Y").date()


class Debt(BaseModel):
    name: str = Field(alias=AliasChoices("name", "Name"))
    current_balance: float = Field(
        alias=AliasChoices("current_balance", "Current Balance")
    )
    monthly: float = Field(alias=AliasChoices("monthly", "Monthly"))
    due_date: datetime.date = Field(alias=AliasChoices("due_date", "Due Date"))
    debt_type: str = Field(alias=AliasChoices("debt_type", "Debt Type"))

    @field_validator(
        "monthly",
        "current_balance",
        mode="before",
    )
    def validate_amount(cls, v):
        return parse_currency(v, pattern)

    @field_validator("due_date", mode="before")
    def validate_due_date(cls, v):
        return datetime.datetime.strptime(v, "%m/%d/%Y").date()


def _parse_file_as_model(file_path: str, model: type[BaseModel]):
    with open(file_path) as f:
        for line in csv.DictReader(f):
            yield model.model_validate(line)


def parse_expense(file_path: str) -> list[Expense]:
    return list(_parse_file_as_model(file_path, Expense))


def parse_income(file_path: str) -> list[Income]:
    return list(_parse_file_as_model(file_path, Income))


def parse_debts(file_path: str) -> list[Debt]:
    return list(_parse_file_as_model(file_path, Debt))
