import pytest
from spacecases.strutils import currency_str_format


def test_currency_str_format_negative_amount():
    with pytest.raises(ValueError):
        currency_str_format(-1)


def test_currency_str_format_zero_amount() -> None:
    assert currency_str_format(0), "$0.00"


def test_currency_str_format_single_digit_cents() -> None:
    assert currency_str_format(1), "$0.01"


def test_currency_str_format_double_digit_cents() -> None:
    assert currency_str_format(49), "$0.49"


def test_currency_str_format_integer_amount() -> None:
    assert currency_str_format(100000), "$1000.00"


def test_currency_str_format_dollar_with_cents() -> None:
    assert currency_str_format(1234), "$12.34"


def test_currency_str_format_bigint_max() -> None:
    assert currency_str_format(9223372036854775807), "$92233720368547758.07"


def test_currency_str_format_huge_number() -> None:
    assert currency_str_format(
        12837461872938172381827372812783728
    ), "$128374618729381723818273728127837.28"
