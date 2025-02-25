WITH capacity_check AS (
    SELECT
        (SELECT COUNT(*) FROM items WHERE owner_id = $1) <
        (SELECT inventory_capacity FROM "users" WHERE id = $1) AS is_within_capacity
)
INSERT INTO items (owner_id, type, name, details)
SELECT $1, $2, $3, $4
FROM capacity_check
WHERE capacity_check.is_within_capacity
RETURNING owner_id;