from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    database_name = os.getenv("MONGODB_DATABASE", "sustainability_dashboard")
    
    db.client = AsyncIOMotorClient(mongodb_url)
    db.database = db.client[database_name]
    
    # Test connection
    try:
        await db.client.admin.command('ping')
        print(f"Connected to MongoDB at {mongodb_url}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

async def get_database():
    """Get database instance"""
    return db.database