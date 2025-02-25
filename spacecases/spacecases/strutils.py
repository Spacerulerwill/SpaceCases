from decimal import Decimal


def currency_str_format(amount: int) -> str:
    return "$" + str((Decimal(amount) / 100).quantize(Decimal("0.01")))
