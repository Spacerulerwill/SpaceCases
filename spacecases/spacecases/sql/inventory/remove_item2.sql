DELETE FROM items
WHERE id = $2 AND owner_id = $1
RETURNING id
