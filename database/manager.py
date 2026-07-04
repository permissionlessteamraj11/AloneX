"""Database manager with support for MongoDB, PostgreSQL, and Redis."""
import logging
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import redis.asyncio as redis
from config import Config
from utils.decorators import log_execution

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Unified database manager for all database operations."""

    def __init__(self, config: Config):
        """Initialize database manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.mongo_db: Optional[AsyncIOMotorDatabase] = None
        self.redis_client: Optional[redis.Redis] = None
        self._is_connected = False

    @log_execution
    async def connect(self) -> None:
        """Connect to all configured databases."""
        try:
            logger.info("Connecting to databases...")
            
            # MongoDB connection
            if self.config.MONGO_URL:
                self.mongo_client = AsyncIOMotorClient(self.config.MONGO_URL)
                self.mongo_db = self.mongo_client["AloneX"]
                await self.mongo_db.command("ping")
                logger.info("✅ Connected to MongoDB")
            
            # Redis connection
            if self.config.REDIS_URL:
                self.redis_client = await redis.from_url(self.config.REDIS_URL)
                await self.redis_client.ping()
                logger.info("✅ Connected to Redis")
            
            self._is_connected = True
            logger.info("✅ All databases connected")
            
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}", exc_info=True)
            raise

    @log_execution
    async def disconnect(self) -> None:
        """Disconnect from all databases."""
        try:
            logger.info("Disconnecting from databases...")
            
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("✅ Disconnected from MongoDB")
            
            if self.redis_client:
                await self.redis_client.close()
                logger.info("✅ Disconnected from Redis")
            
            self._is_connected = False
        except Exception as e:
            logger.error(f"Disconnection error: {str(e)}", exc_info=True)

    # MongoDB Operations
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict]:
        """Find a single document.
        
        Args:
            collection: Collection name
            query: Query filter
            
        Returns:
            Document or None
        """
        if not self.mongo_db:
            return None
        return await self.mongo_db[collection].find_one(query)

    async def find_many(self, collection: str, query: Dict[str, Any]) -> list:
        """Find multiple documents.
        
        Args:
            collection: Collection name
            query: Query filter
            
        Returns:
            List of documents
        """
        if not self.mongo_db:
            return []
        cursor = self.mongo_db[collection].find(query)
        return await cursor.to_list(length=None)

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a document.
        
        Args:
            collection: Collection name
            document: Document to insert
            
        Returns:
            Inserted document ID
        """
        if not self.mongo_db:
            return None
        result = await self.mongo_db[collection].insert_one(document)
        return str(result.inserted_id)

    async def update_one(self, collection: str, query: Dict, update: Dict) -> int:
        """Update a document.
        
        Args:
            collection: Collection name
            query: Query filter
            update: Update document
            
        Returns:
            Number of modified documents
        """
        if not self.mongo_db:
            return 0
        result = await self.mongo_db[collection].update_one(query, {"$set": update})
        return result.modified_count

    async def delete_one(self, collection: str, query: Dict) -> int:
        """Delete a document.
        
        Args:
            collection: Collection name
            query: Query filter
            
        Returns:
            Number of deleted documents
        """
        if not self.mongo_db:
            return 0
        result = await self.mongo_db[collection].delete_one(query)
        return result.deleted_count

    # Redis Operations
    async def redis_set(self, key: str, value: str, ttl: int = None) -> bool:
        """Set a Redis key.
        
        Args:
            key: Redis key
            value: Value
            ttl: Time to live in seconds
            
        Returns:
            Success status
        """
        if not self.redis_client:
            return False
        await self.redis_client.set(key, value, ex=ttl)
        return True

    async def redis_get(self, key: str) -> Optional[str]:
        """Get a Redis value.
        
        Args:
            key: Redis key
            
        Returns:
            Value or None
        """
        if not self.redis_client:
            return None
        return await self.redis_client.get(key)

    async def redis_delete(self, key: str) -> bool:
        """Delete a Redis key.
        
        Args:
            key: Redis key
            
        Returns:
            Success status
        """
        if not self.redis_client:
            return False
        await self.redis_client.delete(key)
        return True

    @property
    def is_connected(self) -> bool:
        """Check if databases are connected."""
        return self._is_connected
