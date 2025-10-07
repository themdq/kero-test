# Kero Test

A compact, async event pipeline built with Python: FastAPI -> Kafka -> Processor -> PostgreSQL.
Designed with interfaces (Messaging / Database), factories, Pydantic v2 validation, and idempotent writes.

---

## Contents

* `receiver/` — FastAPI app that accepts events and publishes them to Kafka.
* `processor/` — worker that consumes from Kafka, validates events, and writes them to Postgres.
* `docker-compose.yml` / `docker-compose.kraft.yml`

---

## Architecture (short)

```
[Client] -> POST /api/v1/events -> [Receiver (FastAPI, producer)] -> Kafka topic -> [Processor (consumer)] -> PostgreSQL (events)
```

## Quickstart (local)

### Requirements

For local run:
* Python 3.13+
* uv
* Docker & Docker Compose (for Kafka + Postgres)

### 1. Clone

```bash
git clone <repo-url>
cd <repo-root>
```

### 2. Create `.env` (example)

```env
POSTGRES_DB=processor
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_PORT=5432

PROJECT_NAME="receiver"
KAFKA_BOOTSTRAP_SERVERS="kafka:9092"
KAFKA_TOPIC="incoming_events"
```

### 3. Bring up infra

```bash
docker compose -f docker-compose.yml up -d
```

OR

```bash
docker compose -f docker-compose.kraft.yml up -d
```

> Note: the first KRaft run must initialize storage.

### 4. Run services locally

Services automatically starts with docker-compose, but you can start them locally

* Create .env.dev
* Create venv and install requirements
```bash
cd receiver
uv sync

cd processor
uv sync
``` 

* Use vscode debug options or run manually:

```bash
# Receiver
cd receiver
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Processor
cd processor
python app/main.py
```

---

## Shortcuts

```bash
poe lint
poe format
poe mypy
poe test
```

---

## Possible improvements

## 1. CI / CD

Github actions / gitlab ci-cd pipeline with stages:

* **Linting & formatting**: `ruff`.
* **Static types**: `mypy`.
* **Tests**: `pytest`.
* **Build**: build Docker images and push to a registry.

---

## 2. Remove ZooKeeper (KRaft)

Modern Kafka distributions support running without ZooKeeper (KRaft mode).

---

## 3. Schema Registry

Add a Schema Registry

---

## 4. Kafka UI

I used **Kafdrop** for simplicity

---

## 5. High Availability

* Use multiple nodes (3+) for kafka, zookeeper, postgres.
* Use reverse proxy for web server

---

## 6. Data validation & types

Decimal type preferred for monetary values

---

## 7. Branching strategy & workflow

I used only one branch, but in prod i will use feature->dev->main strategy

---

## 8. Separate repos for producer & consumer

## 9. Authentication

* Add authentication to the receiver API.

---

## 11. Monitoring & Observability

* Metrics: expose Prometheus metrics (FastAPI + aiokafka exporter; Kafka JMX exporter; Postgres exporter).
* Dashboards: Grafana dashboards for application metrics, Kafka lag, consumer lag, broker health.
* Logging: structured logs, shipped to centralized system (ELK/EFK, Loki).

---

## 12. Backups & Migrations

* Backups and migrations for database

---

## 13. Tests & Quality

* Expand tests: unit, integration, end-to-end.