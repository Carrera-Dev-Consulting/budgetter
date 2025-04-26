from collections import defaultdict
from copy import deepcopy
from functools import cache
from typing import Iterable, TypeVar
from budgetter.parse import Debt


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
        if index == len(items) or value == 0:
            return KnapSack()

        best_value = _knapsack(index + 1, value)
        if value >= items[index].current_balance:
            sack = _knapsack(index + 1, value - items[index].current_balance)
            sack.add_item(items[index])
            best_value = max(best_value, sack)

        return best_value

    return _knapsack(0, limit).items


def find_best_fit(debts: list[Debt], limit: int) -> list[Debt]:
    all_payable_debts = [
        d for d in debts if d.current_balance > 0 and d.current_balance <= limit
    ]
    # sort by balance then by monthly
    all_payable_debts.sort(key=lambda d: (d.current_balance, d.monthly))

    best_sack = knapsack(all_payable_debts, limit)
    return best_sack
