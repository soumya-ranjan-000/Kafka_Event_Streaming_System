import pytest
from app.models import OrderEvent
from datetime import datetime

def test_order_event_validation():
    payload = {
        "eventId": "event-1",
        "orderId": "order-1",
        "customerId": "cust-1",
        "productId": "prod-1",
        "quantity": 2,
        "price": 19.99,
        "status": "CREATED",
        "timestamp": datetime.now().isoformat()
    }
    
    event = OrderEvent(**payload)
    assert event.orderId == "order-1"
    assert event.status == "CREATED"
