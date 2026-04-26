from fastapi import APIRouter, HTTPException
from typing import List
from ..database import get_db
from pydantic import BaseModel, Field

router = APIRouter(prefix="/products", tags=["products"])

class Product(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: str
    price: float
    image: str
    category: str
    stock: int

@router.get("/", response_model=List[Product])
async def get_products():
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not ready")
    
    cursor = db.products.find()
    products = await cursor.to_list(length=100)
    return products
