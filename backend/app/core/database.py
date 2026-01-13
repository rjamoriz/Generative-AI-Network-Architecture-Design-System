"""
Database Connection Management
Handles connections to PostgreSQL, MongoDB, and Redis without hardcoding credentials
"""
from typing import Optional, AsyncGenerator
import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for ORM models
Base = declarative_base()


class DatabaseManager:
    """
    Manages database connections with credential injection
    Supports PostgreSQL, MongoDB, and Redis
    """
    
    def __init__(self):
        """Initialize database manager"""
        self.settings = get_settings()
        
        # PostgreSQL
        self._postgres_engine = None
        self._postgres_session_maker = None
        
        # MongoDB
        self._mongodb_client = None
        self._mongodb_database = None
        
        # Redis
        self._redis_client = None
        
        logger.info("Database manager initialized")
    
    # ==================== PostgreSQL ====================
    
    def get_postgres_engine(self):
        """
        Get PostgreSQL async engine with credentials from config
        Credentials are injected at runtime, never hardcoded
        """
        if self._postgres_engine is None:
            if not self.settings.postgres_url_async:
                raise ValueError("PostgreSQL credentials not configured. Set POSTGRES_* environment variables")
            
            self._postgres_engine = create_async_engine(
                self.settings.postgres_url_async,
                echo=self.settings.debug,
                pool_size=self.settings.postgres_pool_size,
                max_overflow=self.settings.postgres_max_overflow,
                pool_pre_ping=True,
                poolclass=NullPool if self.settings.is_development else None
            )
            
            logger.info(f"PostgreSQL engine created: {self.settings.postgres_host}:{self.settings.postgres_port}")
        
        return self._postgres_engine
    
    def get_postgres_session_maker(self) -> async_sessionmaker:
        """Get PostgreSQL session maker"""
        if self._postgres_session_maker is None:
            engine = self.get_postgres_engine()
            self._postgres_session_maker = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("PostgreSQL session maker created")
        
        return self._postgres_session_maker
    
    @asynccontextmanager
    async def get_postgres_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get PostgreSQL session context manager
        
        Usage:
            async with db_manager.get_postgres_session() as session:
                result = await session.execute(query)
        """
        session_maker = self.get_postgres_session_maker()
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close_postgres(self):
        """Close PostgreSQL connections"""
        if self._postgres_engine:
            await self._postgres_engine.dispose()
            logger.info("PostgreSQL connections closed")
    
    # ==================== MongoDB ====================
    
    def get_mongodb_client(self):
        """
        Get MongoDB client with credentials from config
        Credentials are injected at runtime, never hardcoded
        """
        if self._mongodb_client is None:
            if not self.settings.mongodb_uri:
                raise ValueError("MongoDB credentials not configured. Set MONGODB_URI environment variable")
            
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                
                self._mongodb_client = AsyncIOMotorClient(
                    self.settings.mongodb_uri,
                    serverSelectionTimeoutMS=self.settings.mongodb_timeout
                )
                
                logger.info("MongoDB client created")
                
            except ImportError:
                raise ImportError("motor library required for MongoDB. Install: pip install motor")
        
        return self._mongodb_client
    
    def get_mongodb_database(self):
        """Get MongoDB database"""
        if self._mongodb_database is None:
            client = self.get_mongodb_client()
            self._mongodb_database = client[self.settings.mongodb_database]
            logger.info(f"MongoDB database selected: {self.settings.mongodb_database}")
        
        return self._mongodb_database
    
    def get_mongodb_collection(self, collection_name: Optional[str] = None):
        """
        Get MongoDB collection
        
        Args:
            collection_name: Collection name (defaults to design_embeddings)
        """
        database = self.get_mongodb_database()
        collection_name = collection_name or self.settings.mongodb_collection
        return database[collection_name]
    
    async def close_mongodb(self):
        """Close MongoDB connections"""
        if self._mongodb_client:
            self._mongodb_client.close()
            logger.info("MongoDB connections closed")
    
    # ==================== Redis ====================
    
    async def get_redis_client(self):
        """
        Get Redis client with credentials from config
        Credentials are injected at runtime, never hardcoded
        """
        if self._redis_client is None:
            try:
                import redis.asyncio as aioredis
                
                self._redis_client = await aioredis.from_url(
                    self.settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=self.settings.redis_pool_size,
                    socket_timeout=self.settings.redis_timeout
                )
                
                # Test connection
                await self._redis_client.ping()
                logger.info(f"Redis client created: {self.settings.redis_host}:{self.settings.redis_port}")
                
            except ImportError:
                raise ImportError("redis library required. Install: pip install redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        
        return self._redis_client
    
    async def close_redis(self):
        """Close Redis connections"""
        if self._redis_client:
            await self._redis_client.close()
            logger.info("Redis connections closed")
    
    # ==================== Lifecycle Management ====================
    
    async def connect_all(self):
        """Connect to all databases"""
        logger.info("Connecting to all databases...")
        
        # PostgreSQL
        try:
            self.get_postgres_engine()
            logger.info("✓ PostgreSQL connected")
        except Exception as e:
            logger.error(f"✗ PostgreSQL connection failed: {e}")
        
        # MongoDB
        try:
            self.get_mongodb_client()
            logger.info("✓ MongoDB connected")
        except Exception as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
        
        # Redis
        try:
            await self.get_redis_client()
            logger.info("✓ Redis connected")
        except Exception as e:
            logger.error(f"✗ Redis connection failed: {e}")
    
    async def close_all(self):
        """Close all database connections"""
        logger.info("Closing all database connections...")
        
        await self.close_postgres()
        await self.close_mongodb()
        await self.close_redis()
        
        logger.info("All database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager()
    
    return _db_manager


# Dependency injection for FastAPI
async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for PostgreSQL session
    
    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_postgres_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    db_manager = get_database_manager()
    async with db_manager.get_postgres_session() as session:
        yield session


async def get_mongodb_database():
    """
    FastAPI dependency for MongoDB database
    
    Usage:
        @app.get("/designs")
        async def get_designs(db = Depends(get_mongodb_database)):
            designs = await db.designs.find().to_list(100)
            return designs
    """
    db_manager = get_database_manager()
    return db_manager.get_mongodb_database()


async def get_redis_client():
    """
    FastAPI dependency for Redis client
    
    Usage:
        @app.get("/cached")
        async def get_cached(redis = Depends(get_redis_client)):
            value = await redis.get("key")
            return {"value": value}
    """
    db_manager = get_database_manager()
    return await db_manager.get_redis_client()
