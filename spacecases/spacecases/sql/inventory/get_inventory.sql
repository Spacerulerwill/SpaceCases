SELECT id, name, type, details FROM items
WHERE owner_id = $1;