WITH user_exists AS (
    SELECT EXISTS (SELECT 1 FROM "users" WHERE id = $1 FOR UPDATE) AS user_exists
),
item AS (
    SELECT name, type, details
    FROM items
    WHERE owner_id = $1 AND id = $2
)
SELECT 
    (SELECT user_exists FROM user_exists) AS user_exists,
    CASE WHEN EXISTS (SELECT 1 FROM item) 
         THEN ROW(item.name, item.type, item.details) 
         ELSE NULL 
    END AS item_details
FROM user_exists
LEFT JOIN item ON true
LIMIT 1;
