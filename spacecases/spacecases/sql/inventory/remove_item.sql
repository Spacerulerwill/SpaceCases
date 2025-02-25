WITH user_exists AS (
    SELECT EXISTS (SELECT 1 FROM users WHERE id = $1 FOR UPDATE) AS user_exists
),
item_owned AS (
    SELECT EXISTS (SELECT 1 FROM items WHERE id = $2 AND owner_id = $1 FOR UPDATE) AS item_owned
),
delete_item AS (
    DELETE FROM items
    WHERE id = $2 AND owner_id = $1
    RETURNING id
)
SELECT 
    (SELECT user_exists FROM user_exists) AS user_exists,
    (SELECT item_owned FROM item_owned) AS item_owned;
