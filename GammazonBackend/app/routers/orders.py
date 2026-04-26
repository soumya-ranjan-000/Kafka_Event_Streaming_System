from fastapi import APIRouter, HTTPException
from typing import List, Optional
import httpx
from datetime import datetime
from ..database import get_db
from ..config import settings
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderRequest(BaseModel):
    customerId: str
    productId: str
    quantity: int
    price: float

class OrderDB(BaseModel):
    id: str = Field(alias="_id")
    event_id: str
    customer_id: str
    product_id: str
    quantity: int
    price: float
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    model_config = ConfigDict(populate_by_name=True)

@router.get("/", response_model=List[OrderDB])
async def get_orders():
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not ready")
    
    cursor = db.orders.find().sort("created_at", -1)
    orders = await cursor.to_list(length=100)
    return orders

@router.post("/")
async def create_order(order: OrderRequest):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.producer_url,
                json=order.model_dump(),
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Failed to reach Producer: {str(e)}")
