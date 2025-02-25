UPDATE items
SET 
    type = $3,
    name = $4,
    details = $5
WHERE id = $2
  AND owner_id = $1
RETURNING id;
