CREATE TABLE IF NOT EXISTS tmp_purchases (
    supermarket_id VARCHAR(20),
    timestamp TIMESTAMP,
    user_id UUID,
    items_list TEXT,
    total_amount NUMERIC(10, 2)
);

COPY tmp_purchases(
    supermarket_id,
    timestamp,
    user_id,
    items_list,
    total_amount
)
FROM '/docker-entrypoint-initdb.d/purchases.csv' WITH (FORMAT csv, HEADER true);
INSERT INTO users(id, first_purchase, purchase_count)
SELECT user_id,
    MIN(timestamp) AS first_purchase,
    COUNT(*) AS purchase_count
FROM tmp_purchases
GROUP BY user_id ON CONFLICT (id) DO
UPDATE
SET purchase_count = users.purchase_count + EXCLUDED.purchase_count;

INSERT INTO purchases(
        supermarket_id,
        timestamp,
        user_id,
        items_list,
        total_amount
    )
SELECT supermarket_id,
    timestamp,
    user_id,
    items_list,
    total_amount
FROM tmp_purchases;

DROP TABLE tmp_purchases;