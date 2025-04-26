from budgetter.parse import Debt
from budgetter.best_fit import knapsack


def create_debt(
    value: float,
    weight: float,
    name: str,
):
    return Debt(
        current_balance=weight,
        monthly=value,
        name=name,
        due_date="10/10/2022",
        debt_type="Payday Loan",
    )


def test_knapsack__when_given_empty_sack__best_sack_is_empty():
    best_sack = knapsack([], 0)
    assert best_sack == []


def test_knapsack__when_given_simple_sack__calculates_best_as_expected():
    first = create_debt(100, 100, "debt")
    best_sack = knapsack(
        [
            first,
            create_debt(200, 150, "debt"),
        ],
        100,
    )
    assert best_sack == [first]


def test_knapsack__when_given_simple_sack_with_most_expensive_item_in_range__returns_item():
    selected = create_debt(200, 150, "debt")
    best_sack = knapsack(
        [
            create_debt(100, 100, "debt"),
            selected,
        ],
        150,
    )
    assert best_sack == [selected]


def test_knapsack__when_given_realistic_example__returns_best_fit():
    best_sack = knapsack(
        [
            create_debt(50, 100, "debt"),
            create_debt(150, 150, "debt"),
            create_debt(50, 50, "debt"),
            create_debt(25, 25, "debt"),
            create_debt(25, 25, "debt"),
        ],
        150,
    )
    assert best_sack == [create_debt(150, 150, "debt")]
