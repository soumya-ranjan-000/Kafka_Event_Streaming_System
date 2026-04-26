# E-Commerce Message Queue System: Architecture & Workflow Guide

Welcome to the documentation for our E-Commerce Message Queue implementation. This guide is designed for graduate students and developers to understand the practical workflow of a robust, production-ready event-driven system using Apache Kafka.

---

## 1. Introduction and Use Case

In a typical e-commerce platform, when a user clicks "Checkout", several things must happen:
1. Payment processing
2. Inventory deduction
3. Shipping label generation
4. Notification dispatch

If the checkout service tries to do all of these synchronously, the system becomes slow, deeply coupled, and prone to catastrophic failure (e.g., if the email server is down, the user cannot buy the item). 

**The Solution:** We introduce a Message Queue (Kafka). The `Checkout Service (Producer)` simply drops an "Order Created" event into the queue and immediately returns a "Success" response to the user. Various downstream services, like our `Order Processor (Consumer)`, pick up this message at their own pace and do the heavy lifting asynchronously.

---

## 2. Core Concepts Demonstrated

### A. Producers and Consumers
*   **Producer (Spring Boot / Java):** The service generating data. It exposes an API (`POST /api/orders`) for users to create orders. Once an order is received, it pushes an `OrderEvent` to the Kafka `orders-topic`.
*   **Consumer (FastAPI / Python):** The "workhorse." It continuously listens (polls) the `orders-topic`. When an event arrives, it processes it (validates it and saves it to MongoDB), changing the order status from `PENDING` to `PROCESSED`.

### B. Idempotency (Exactly-Once Processing)
In distributed systems, networks are unreliable. Kafka guarantees "at-least-once" delivery, meaning a consumer might receive the exact same message twice. **Idempotency** is the system's ability to handle duplicate messages without creating duplicate side effects (e.g., charging a user twice).
*   **Producer-side:** We configured `ENABLE_IDEMPOTENCE_CONFIG = "true"`. Kafka tracks sequence numbers to ensure the producer doesn't accidentally duplicate messages during internal retries.
*   **Consumer-side:** We use the `orderId` as the unique `_id` primary key in MongoDB. If a duplicate message is consumed, MongoDB throws a `DuplicateKeyError`. The consumer traps this error, safely ignores it, and acknowledges the message.

### C. Manual Offset Management (Data Safety)
Offsets represent a consumer's "bookmark" in the queue. 
By default, Kafka uses "auto-commit", which means it moves the bookmark forward as soon as it gives the message to the consumer. If the consumer crashes before saving to the database, that order is lost forever.
*   **Our Solution:** We disabled auto-commit. The consumer only manually commits the offset (`await consumer.commit()`) **after** the order is safely persisted in MongoDB.

### D. Resilience: Retries and Dead Letter Queues (DLQ)
*   **Retries with Exponential Backoff:** If the database goes down momentarily, the consumer shouldn't instantly fail. It uses the `tenacity` library to retry the database insert 5 times, waiting longer between each attempt (2s, 4s, 8s...).
*   **Dead Letter Queue (DLQ):** If a "poison pill" arrives (e.g., a fundamentally corrupted JSON message that will never pass validation), retrying is useless. The consumer catches the validation error, routes the bad message to a special `orders-topic.dlq` topic, and commits the offset. This prevents the queue from getting "stuck" on a bad message.

---

## 3. Project Architecture & File Details

### Tech Stack
*   **Message Broker:** Apache Kafka & Zookeeper
*   **Producer:** Java 17, Spring Boot 3, Spring Kafka
*   **Consumer:** Python 3.11, FastAPI, AIOKafka, Pydantic, Motor (Async MongoDB)
*   **Database:** MongoDB 6.0
*   **Infrastructure:** Docker Compose

### Directory Structure & File Roles

#### Root Directory
*   `docker-compose.yml`: The orchestrator. It boots up Zookeeper, Kafka, Kafka-UI, MongoDB, the Producer App, and the Consumer App in an isolated virtual network.

#### The Producer (`/KafkaProducer`)
*   **`config/KafkaProducerConfig.java`**: Bootstraps the Kafka connection. Contains production settings like `ENABLE_IDEMPOTENCE_CONFIG`, `ACKS_CONFIG = "all"` (requiring all broker replicas to acknowledge the message), and serialization logic.
*   **`controller/OrderController.java`**: The REST endpoint `POST /api/orders`. Maps HTTP JSON payloads to an internal `OrderEvent`.
*   **`service/OrderService.java`**: Uses Spring's `KafkaTemplate` to asynchronously publish the event to Kafka and handles success/failure logging callbacks.
*   **`model/*.java`**: POJOs representing the Request, Event, and Response.

#### The Consumer (`/KafkaConsumer`)
*   **`app/consumer.py`**: The heart of the Python app. Contains the `AIOKafkaConsumer` polling loop. Handles JSON parsing, triggering retries, catching `DuplicateKeyError` for idempotency, routing poison pills to the DLQ, and executing manual offset commits.
*   **`app/database.py`**: Connects to MongoDB asynchronously using `motor` and ensures the database is ready for idempotency.
*   **`app/models.py`**: Strict Pydantic models. They validate incoming Kafka bytes into structured Python objects, throwing `ValueErrors` for bad data (which triggers the DLQ).
*   **`app/routers/orders.py`**: Exposes `GET /api/orders` so users can query the database to prove the consumer actually did its job.
*   **`app/main.py`**: The FastAPI entry point. It uses "Lifespan" events to start the Kafka consumer in a background async task when the API server boots up, and cleanly shuts it down on exit.

---

## 4. How to Run and Demonstrate

**1. Spin up the cluster:**
From the root directory containing `docker-compose.yml`:
```bash
docker-compose up --build -d
```

**2. Observe the infrastructure:**
Navigate to `http://localhost:8081` in your browser. This is the Kafka UI. You will see the `orders-topic` and `orders-topic.dlq` created automatically.

**3. Produce a Message (Happy Path):**
```bash
curl -X POST http://localhost:8080/api/orders \
-H "Content-Type: application/json" \
-d '{
  "customerId": "CUST-001",
  "productId": "PROD-A",
  "quantity": 5,
  "price": 49.99
}'
```
*Result:* The Spring Boot app returns an immediate 201 Created. In the background, the message hits Kafka, the Python consumer picks it up, validates it, and saves it to MongoDB.

**4. Verify the Consumer:**
```bash
curl http://localhost:8000/api/orders/
```
*Result:* You will see the order persisted with `status: "PROCESSED"`.

**5. Testing Advanced Scenarios:**
*   **Testing Idempotency:** If you could force Kafka to resend the exact same `orderId`, you would see a log line in the Consumer console: `Duplicate message detected (Idempotency). Committing offset and ignoring.`
*   **Testing DLQ:** If you manually produce a malformed string directly into the `orders-topic` using the Kafka UI console, the Consumer will log a JSON decode error, skip saving it to MongoDB, and publish that exact string to `orders-topic.dlq`.
