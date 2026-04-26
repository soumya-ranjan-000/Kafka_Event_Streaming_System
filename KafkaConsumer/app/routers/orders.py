from fastapi import APIRouter, HTTPException
from typing import List
from ..database import get_db
from ..models import OrderDB

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.get("/", response_model=List[OrderDB])
async def get_orders(skip: int = 0, limit: int = 10):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    cursor = db.orders.find().skip(skip).limit(limit)
    orders = await cursor.to_list(length=limit)
    return orders

@router.get("/{order_id}", response_model=OrderDB)
async def get_order(order_id: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    order = await db.orders.find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return order
