COPY products(name, unit_price)
FROM '/docker-entrypoint-initdb.d/products_list.csv' WITH (FORMAT csv, HEADER true);