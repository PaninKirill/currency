from decimal import Decimal


def to_decimal(num) -> Decimal:
    return round(Decimal(num), 2)
