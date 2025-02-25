INSERT INTO "users" (id, last_claim, claim_streak, balance, inventory_capacity)
VALUES (($1), '0001-01-01', 0, 0, 5)
ON CONFLICT DO NOTHING
RETURNING id;

