CREATE TABLE IF NOT EXISTS supermarkets (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    first_purchase TIMESTAMP,
    purchase_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    name VARCHAR(100) PRIMARY KEY,
    unit_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    supermarket_id VARCHAR(20) NOT NULL REFERENCES supermarkets(id),
    timestamp TIMESTAMP NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    items_list TEXT NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL
);