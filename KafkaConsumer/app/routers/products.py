from fastapi import APIRouter, HTTPException
from typing import List
from ..database import get_db
from ..models import Product

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=List[Product])
async def get_products():
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    cursor = db.products.find()
    products = await cursor.to_list(length=100)
    return products

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    product = await db.products.find_one({"_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return product
