WITH claim_streak AS (
    SELECT
        CASE 
            WHEN last_claim::date = CURRENT_DATE - INTERVAL '1 day' THEN
                claim_streak + 1 --Increase streak if last claim was yesterday
            WHEN last_claim::date < CURRENT_DATE - INTERVAL '1 day' THEN
                1 -- Reset streak if break more than 1 day
            ELSE
                claim_streak  -- Keep current streak if claim is made today
        END AS new_streak,
        last_claim::date < CURRENT_DATE AS can_claim
    FROM
        "users"
    WHERE
        id = $1
    FOR UPDATE
),
claim_amount AS (
    SELECT
        LEAST(10000 + (claim_streak.new_streak - 1) * 2000, 30000) AS amount
    FROM
        claim_streak
),
updated_user AS (
    UPDATE
        "users"
    SET
        last_claim = CURRENT_DATE,
        balance = balance + claim_amount.amount,
        claim_streak = claim_streak.new_streak
    FROM
        claim_amount,
        claim_streak
    WHERE
        id = $1
        AND claim_streak.can_claim
    RETURNING
        balance,
        claim_streak.new_streak,
        claim_amount.amount
)
SELECT 
    claim_streak.can_claim AS claimed, 
    updated_user.balance,
    updated_user.new_streak,
    updated_user.amount
FROM claim_streak
LEFT JOIN updated_user
ON TRUE;
