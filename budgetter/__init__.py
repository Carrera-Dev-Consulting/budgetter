from collections import defaultdict
import csv
import datetime
import click

from budgetter.account import Account
from budgetter.budget import Budget
from budgetter.parse import (
    Debt,
    Expense,
    Income,
    parse_expense,
    parse_debts,
    parse_income,
    _parse_file_as_model,
)
from budgetter.transaction import Transaction


@click.group()
def main():
    pass


@main.command()
@click.option(
    "-f",
    "--forecast",
    type=click.Path(
        exists=False,
        dir_okay=False,
        readable=True,
    ),
    help="File with forecasted transactions",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        exists=False,
        dir_okay=False,
        writable=True,
    ),
    default="output.csv",
    help=("Output file path (default: %(default)s)"),
)
def balance_sheet(
    forecast: str,
    output: str,
):
    checking = Account(
        transactions=_parse_file_as_model(forecast, Transaction),
        name="Checking",
    )
    unique_days = set(t.when.date() for t in checking.transactions)
    unique_days = sorted(unique_days)
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "balance"])
        writer.writeheader()

        for day in unique_days:
            balance = checking.balance_on_day(day)
            writer.writerow({"date": day, "balance": f"{balance:.2f}"})


@main.command()
@click.option(
    "-d",
    "--debts",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    help="List of debts",
    required=True,
)
@click.option(
    "-e",
    "--expenses",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    help="List of expenses",
    required=True,
)
@click.option(
    "-i",
    "--incomes",
    type=click.Path(
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    help="List of incomes",
    required=True,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(
        exists=False,
        dir_okay=False,
        writable=True,
    ),
    default="output.csv",
    help="Output file with all the transactions",
)
@click.argument(
    "starting-balance",
    type=click.FloatRange(min=0),
)
@click.argument(
    "end-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
)
def forecast(
    debts: str,
    expenses: str,
    incomes: str,
    starting_balance: float,
    end_date: datetime.date,
    output: str,
):
    budget = Budget()
    checking = Account(name="checking")
    checking.submit_transaction("Me", starting_balance, "initial deposit")
    budget.add_account(checking)

    for expense in parse_expense(expenses):
        handle_expenses(budget, checking, expense)

    for debt in parse_debts(debts):
        handle_debts(budget, checking, debt)

    for income in parse_income(incomes):
        handle_incomes(budget, checking, income)
    forecasted = budget.forecast_account("checking", end_date)
    with open(output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=Transaction.model_fields.keys())
        writer.writeheader()

        for transaction in forecasted.sorted_transactions:
            writer.writerow(transaction.model_dump(mode="json"))

    print("Ending Balance: ", forecasted.balance)


def handle_expenses(budget: Budget, checking: Account, expense: Expense):
    budget.add_payment_schedule(
        expense.name,
        checking,
        "monthly",
        -expense.monthly,
        expense.due_date,
    )


def handle_debts(budget: Budget, checking: Account, debt: Debt):
    debt_account = Account(name=debt.name)
    debt_account.submit_transaction(
        "Me",
        -debt.current_balance,
        "initial deposit",
    )
    budget.add_account(debt_account)
    budget.add_transfer_schedule(
        checking,
        debt_account,
        "monthly",
        debt.name,
        debt.monthly,
        debt.due_date,
    )
    budget.add_transfer_schedule(
        debt_account,
        checking,
        "bi-weekly" if debt.debt_type == "Payday Loan" else "monthly",
        debt.name,
        -debt.monthly,
        debt.due_date,
    )


def handle_incomes(budget: Budget, checking: Account, income: Income):
    budget.add_payment_schedule(
        income.name,
        checking,
        "bi-weekly",
        income.amount,
        income.pay_date,
    )
