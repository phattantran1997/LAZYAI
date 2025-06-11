from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
# Uses database name from URI or defaults to 'test'
db = client.get_default_database()