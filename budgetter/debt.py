import enum


class InterestIntervals(enum.Enum):
    DAILY = 365
    WEEKLY = 52
    MONTHLY = 12
    QUARTERLY = 4
    YEARLY = 1


def calc_interest(principal: float, apr: float, interval: InterestIntervals):
    return principal * (apr / interval.value)
