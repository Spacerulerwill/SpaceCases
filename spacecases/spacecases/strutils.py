def currency_str_format(amount: int) -> str:
    if amount < 0:
        raise ValueError("Amount must be greater than or equal to 0")
    amount_str = str(amount)
    if len(amount_str) <= 2:
        formatted_amount = "0." + amount_str.zfill(2)
    else:
        dollars = amount_str[:-2]
        cents = amount_str[-2:]
        formatted_amount = f"{dollars}.{cents}"
    return f"${formatted_amount}"
