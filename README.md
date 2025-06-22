# Super-Market-App

Microservices application deployed with Docker Compose, simulating a Point Of Sale (POS Simulator) and a Reporting Service for a supermarket chain.


## Prerequisites

- Docker & Docker Compose installed.
- Git.

## Installation and Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/Guy-Keinan/Super-Market-App.git
   cd Super-Market-App
   ```
2. Start all services in detached mode:
   ```bash
   docker compose up -d
   ```
3. The following services will be available:
   - **app_a** (POS Simulator) at `http://localhost:8000`
   - **app_b** (Reporting Service) at `http://localhost:8001`

## Database Initialization

On first startup, the `db` service will run all scripts in `db/initdb/`:

- `01_schema.sql`: creates tables (`supermarkets`, `users`, `products`, `purchases`).
- `02_products.sql`: bulk loads `products_list.csv`.
- `03_purchases.sql`: bulk loads `purchases.csv`, updates `users` table counters.

When using the ORM (SQLAlchemy), the application code also ensures tables exist by running:

```python
# in app_a and app_b on startup
Base.metadata.create_all(bind=engine.sync_engine)
``` 

> **Note:** this uses SQLAlchemy’s metadata to create any missing tables without dropping existing data.

## Running the Services

After `docker compose up -d`, you can interact with each API:

### app_a (POS Simulator)

**Create a purchase**

```bash
curl -X POST http://localhost:8000/purchase \
  -H 'Content-Type: application/json' \
  -d '{"supermarket_id":"SMKT001","items":["milk","bread"]}'
```

Response:
```json
{ "user_id": "<uuid>", "total_amount": 3.5 }
```

### app_b (Reporting Service)

**Unique customers**
```bash
curl http://localhost:8001/stats/unique_customers
```

**Loyal customers (>=3 purchases)**
```bash
curl http://localhost:8001/stats/loyal_customers
```

**Top-selling products**
```bash
curl http://localhost:8001/stats/top_products
```

## Running Tests

### app_a

```bash
docker compose run --rm app_a pytest
```

### app_b

```bash
docker compose run --rm app_b pytest
```