WITH balance_checker AS (
    -- Check if the user has enough balance
    SELECT
        id,
        balance >= $2 AS has_enough
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
SELECT has_enough as deducted
FROM balance_checker;

