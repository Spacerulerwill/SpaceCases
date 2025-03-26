WITH balance_checker AS (
    -- Check if the user has enough balance
    SELECT
        id,
        balance >= $2 AS has_enough,
        balance AS balance_before_transaction
    FROM
        "users"
    WHERE
        id = $1
    FOR UPDATE
),
updated_user AS (
    -- Deduct balance if the user has enough
    UPDATE
        "users"
    SET
        balance = balance - $2
    FROM
        balance_checker
    WHERE
        "users".id = $1
        AND balance_checker.has_enough
)
SELECT 
    balance_checker.has_enough AS deducted,
    balance_checker.balance_before_transaction
FROM 
    balance_checker;
