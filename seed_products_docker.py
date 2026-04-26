import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "ecommerce_db"

products = [
    {
        "_id": "p1",
        "name": "Neural Link Pro",
        "description": "Next-gen brain-computer interface with 10ms latency. High-fidelity neural feedback for seamless integration.",
        "price": 2499.99,
        "image": "https://images.unsplash.com/photo-1558655146-d09347e92766?q=80&w=1000&auto=format&fit=crop",
        "category": "Tech",
        "stock": 50
    },
    {
        "_id": "p2",
        "name": "Quantum Processor X1",
        "description": "Desktop-grade quantum computing module. 128 qubits of pure processing power for complex simulations.",
        "price": 12999.00,
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000&auto=format&fit=crop",
        "category": "Tech",
        "stock": 10
    },
    {
        "_id": "p3",
        "name": "Aero-Lite Sneakers",
        "description": "Gravity-defying footwear with active suspension. Perfect for urban explorers and athletes.",
        "price": 349.50,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1000&auto=format&fit=crop",
        "category": "Fashion",
        "stock": 120
    },
    {
        "_id": "p4",
        "name": "Zenith VR Headset",
        "description": "8K per eye resolution with full body haptic feedback. Experience reality like never before.",
        "price": 899.00,
        "image": "https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?q=80&w=1000&auto=format&fit=crop",
        "category": "Tech",
        "stock": 75
    },
    {
        "_id": "p5",
        "name": "Titanium Smart Watch",
        "description": "Rugged build with 30-day battery life and health monitoring sensors including blood oxygen and ECG.",
        "price": 599.00,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=1000&auto=format&fit=crop",
        "category": "Tech",
        "stock": 200
    },
    {
        "_id": "p6",
        "name": "Nebula Gaming Chair",
        "description": "Zero-gravity ergonomic design with integrated sound system and RGB lighting.",
        "price": 750.00,
        "image": "https://images.unsplash.com/photo-1616627141141-4e1e3370ed21?q=80&w=1000&auto=format&fit=crop",
        "category": "Lifestyle",
        "stock": 30
    }
]

async def seed():
    print(f"Connecting to MongoDB at {MONGODB_URI}...")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    try:
        # Wait for MongoDB to be ready
        for i in range(10):
            try:
                await client.admin.command('ping')
                break
            except Exception:
                print(f"Waiting for MongoDB... ({i+1}/10)")
                await asyncio.sleep(2)
        
        # Drop products first to refresh data if needed
        print("Refreshing products collection...")
        await db.products.drop()

        print(f"Seeding {len(products)} products...")
        await db.products.insert_many(products)
        print("Seeding complete!")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(seed())
