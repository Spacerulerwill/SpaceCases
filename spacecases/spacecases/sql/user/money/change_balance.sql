-- change a user's balance
UPDATE "users"
SET balance = balance + $2
WHERE id = $1
RETURNING id, balance
