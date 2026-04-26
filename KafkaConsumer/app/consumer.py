import json
import logging
import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pymongo.errors import DuplicateKeyError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import ValidationError
from .config import settings
from .models import OrderEvent, OrderDB
from .database import get_db
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    pass

class OrderConsumer:
    def __init__(self):
        self.consumer = None
        self.producer = None
        self.processed_count = 0
        self._running = False

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_consumer_group,
            enable_auto_commit=False,
            auto_offset_reset="earliest"
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers
        )
        
        # Retry logic for initial bootstrap
        max_retries = 10
        for i in range(max_retries):
            try:
                logger.info(f"Connecting to Kafka at {settings.kafka_bootstrap_servers}... (Attempt {i+1}/{max_retries})")
                await self.consumer.start()
                await self.producer.start()
                break
            except Exception as e:
                if i == max_retries - 1:
                    logger.error(f"Failed to connect to Kafka after {max_retries} attempts. Exiting.")
                    raise e
                logger.warning(f"Kafka not ready yet: {e}. Retrying in 5s...")
                await asyncio.sleep(5)
        
        self._running = True
        asyncio.create_task(self.consume())
        logger.info("Kafka consumer started")

    async def stop(self):
        self._running = False
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        logger.info("Kafka consumer stopped")

    async def consume(self):
        try:
            while self._running:
                result = await self.consumer.getmany(timeout_ms=1000)
                for tp, messages in result.items():
                    for msg in messages:
                        await self.process_message(msg)
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")

    async def process_message(self, msg):
        correlation_id = None
        if msg.headers:
            for key, value in msg.headers:
                if key == "X-Correlation-Id":
                    correlation_id = value.decode("utf-8")
        
        raw_payload = msg.value.decode("utf-8")
        try:
            payload = json.loads(raw_payload)
            order_event = OrderEvent(**payload)
            
            await self._save_to_db_with_retry(order_event, correlation_id)
            
            # Manual commit after successful db insertion
            await self.consumer.commit()
            self.processed_count += 1
            logger.info(f"Successfully processed and committed order: {order_event.orderId}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}. Payload: {raw_payload}")
            await self.send_to_dlq(msg.value, correlation_id, str(e))
            await self.consumer.commit()
        except ValidationError as e:
            logger.error(f"Validation error for message: {e}. Payload: {raw_payload}")
            await self.send_to_dlq(msg.value, correlation_id, str(e))
            await self.consumer.commit()
        except DuplicateKeyError:
            logger.info("Duplicate message detected (Idempotency). Committing offset and ignoring.")
            await self.consumer.commit()
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Payload: {raw_payload}")
            await self.send_to_dlq(msg.value, correlation_id, str(e))
            await self.consumer.commit()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(DatabaseError)
    )
    async def _save_to_db_with_retry(self, order_event: OrderEvent, correlation_id: str):
        db = get_db()
        if db is None:
            raise DatabaseError("Database connection not ready")
            
        try:
            order_db = OrderDB(
                _id=order_event.orderId,
                event_id=order_event.eventId,
                customer_id=order_event.customerId,
                product_id=order_event.productId,
                quantity=order_event.quantity,
                price=order_event.price,
                status="PROCESSED",
                created_at=order_event.timestamp,
                processed_at=datetime.utcnow(),
                correlation_id=correlation_id
            )
            
            await db.orders.insert_one(order_db.model_dump(by_alias=True))
            
            # Update product stock
            await db.products.update_one(
                {"_id": order_event.productId},
                {"$inc": {"stock": -order_event.quantity}}
            )
            logger.info(f"Updated stock for product: {order_event.productId}")
        except DuplicateKeyError:
            raise  # Handled by caller to enforce idempotency
        except Exception as e:
            logger.error(f"Database insertion failed: {e}")
            raise DatabaseError(str(e)) # Trigger retry

    async def send_to_dlq(self, payload: bytes, correlation_id: str, error_msg: str):
        headers = []
        if correlation_id:
            headers.append(("X-Correlation-Id", correlation_id.encode("utf-8")))
        headers.append(("error", error_msg.encode("utf-8")))
        
        await self.producer.send_and_wait(
            settings.kafka_dlq_topic,
            value=payload,
            headers=headers
        )
        logger.info(f"Message sent to DLQ topic {settings.kafka_dlq_topic}")

order_consumer = OrderConsumer()
