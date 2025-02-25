from spacecases.strutils import currency_str_format


def test_currency_str_format() -> None:
    assert currency_str_format(50) == "$0.50"
