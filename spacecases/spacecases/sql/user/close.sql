-- removes user from table
DELETE FROM "users"
WHERE id = $1
RETURNING
    id;

