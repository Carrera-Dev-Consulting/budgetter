from copy import deepcopy
from functools import cache
from typing import Iterable, TypeVar
from budgetter.parse import Debt
from enum import Enum


class FitChoice(str, Enum):
    MONTHLY_SAVINGS = "monthly-savings"
    MOST_DEBTS = "most-debts"


class KnapSack:
    items: list[Debt]

    def __init__(self, items: list[Debt] = None):
        self.items = items or []

    def add_item(self, item):
        self.items.append(item)

    def copy(self):
        return KnapSack(deepcopy(self.items))

    def __lt__(self, other):
        return self.value < other.value

    def __gt___(self, other):
        return self.value > other.value

    def __eq__(self, value):
        return isinstance(value, KnapSack) and self.value == value.value

    @property
    def value(self):
        return sum(i.monthly for i in self.items)

    @property
    def weight(self):
        return sum(i.current_balance for i in self.items)


TValue = TypeVar("TValue")


def subsets(items: list[TValue]) -> Iterable[list[TValue]]:
    for i in range(len(items)):
        yield items[:i]


def knapsack(items: list[Debt], limit: int) -> list[Debt]:
    @cache
    def _knapsack(index: int, value: int) -> KnapSack:
        if index == len(items) or value <= 0:
            return KnapSack()

        best_value = _knapsack(index + 1, value)
        if value >= items[index].current_balance:
            sack = _knapsack(index + 1, value - items[index].current_balance)
            sack.add_item(items[index])
            best_value = max(best_value, sack)

        return best_value

    return _knapsack(0, limit).items


def find_best_fit(
    debts_to_payoff: list[Debt],
    limit: float,
    kind: FitChoice = FitChoice.MONTHLY_SAVINGS,
) -> list[Debt]:
    all_payable_debts = [
        d
        for d in debts_to_payoff
        if d.current_balance > 0 and d.current_balance <= limit
    ]

    if kind == FitChoice.MOST_DEBTS:
        # Basically we just want to clear as many as we can
        all_payable_debts.sort(key=lambda d: d.current_balance)
        total = 0
        debts_to_payoff = []
        while total < limit and len(all_payable_debts) > 0:
            if total + all_payable_debts[0].current_balance > limit:
                break
            total += all_payable_debts[0].current_balance
            debts_to_payoff.append(all_payable_debts.pop(0))
        return debts_to_payoff

    # sort by balance then by monthly
    all_payable_debts.sort(key=lambda d: (d.current_balance, d.monthly))

    best_sack = knapsack(all_payable_debts, limit)
    return best_sack
