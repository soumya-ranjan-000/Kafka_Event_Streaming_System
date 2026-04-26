from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class OrderEvent(BaseModel):
    eventId: str
    orderId: str
    customerId: str
    productId: str
    quantity: int
    price: float
    status: str
    timestamp: datetime

class OrderDB(BaseModel):
    id: str = Field(alias="_id")
    event_id: str
    customer_id: str
    product_id: str
    quantity: int
    price: float
    status: str
    created_at: datetime
    processed_at: datetime
    correlation_id: Optional[str] = None
    
class Product(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: str
    price: float
    image: str
    category: str
    stock: int

    model_config = ConfigDict(populate_by_name=True)
