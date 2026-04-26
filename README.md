# Gammazon: Event-Driven E-Commerce Platform

Gammazon is a microservices-based e-commerce application that demonstrates real-time event streaming using Apache Kafka. The system is designed to showcase modern event-driven architecture patterns for scalable and resilient online retail platforms.

## Key Features
- **Microservices Architecture:** Separate services for frontend, backend, Kafka producer, and Kafka consumer, each in its own container.
- **Event Streaming:** Uses Apache Kafka to stream order and product events between services for real-time processing.
- **Polyglot Implementation:** Combines Java (Spring Boot) for the producer, Python (FastAPI) for backend and consumer, and JavaScript (React + Vite) for the frontend.
- **Dockerized:** All components are containerized for easy deployment and orchestration using Docker Compose.
- **Database Integration:** Supports persistent storage for products and orders.

## Components
- **GammazonFrontend:** React-based user interface for browsing products and placing orders.
- **GammazonBackend:** FastAPI service for handling API requests, business logic, and database operations.
- **KafkaProducer:** Java Spring Boot service that produces order events to Kafka topics.
- **KafkaConsumer:** Python service that consumes events from Kafka and updates the database accordingly.

## Usage
- Start all services with Docker Compose.
- Place orders and view real-time updates as events flow through Kafka.

## Purpose
This project is intended for learning, demonstration, and experimentation with event-driven microservices, Kafka, and containerized deployments in a modern e-commerce context.
