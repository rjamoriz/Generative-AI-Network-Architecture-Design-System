"""
External Database Connector
Connects to external databases containing historical network design and validation data
"""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import oracledb

from app.core.config import settings
from app.models.network_design import NetworkDesign, DesignStatus

logger = logging.getLogger(__name__)


class ExternalDatabaseConnector:
    """
    Connector for external databases with historical design data
    Supports PostgreSQL, Oracle, and MongoDB external sources
    """
    
    def __init__(self):
        """Initialize external database connector"""
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.oracle_pool: Optional[Any] = None
        
        logger.info("External database connector initialized")
    
    async def connect_postgresql(self, connection_string: str) -> bool:
        """
        Connect to external PostgreSQL database
        
        Args:
            connection_string: PostgreSQL connection string
        
        Returns:
            True if successful
        """
        try:
            self.pg_pool = await asyncpg.create_pool(
                connection_string,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            
            logger.info("Connected to external PostgreSQL database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    async def connect_mongodb(self, connection_string: str, database: str) -> bool:
        """
        Connect to external MongoDB database
        
        Args:
            connection_string: MongoDB connection string
            database: Database name
        
        Returns:
            True if successful
        """
        try:
            self.mongo_client = AsyncIOMotorClient(connection_string)
            # Test connection
            await self.mongo_client[database].command('ping')
            
            logger.info(f"Connected to external MongoDB database: {database}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def connect_oracle(self, connection_string: str) -> bool:
        """
        Connect to external Oracle database
        
        Args:
            connection_string: Oracle connection string
        
        Returns:
            True if successful
        """
        try:
            self.oracle_pool = oracledb.create_pool(
                dsn=connection_string,
                min=2,
                max=10,
                increment=1
            )
            
            logger.info("Connected to external Oracle database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Oracle: {e}")
            return False
    
    async def query_historical_designs_pg(self,
                                         filters: Dict[str, Any],
                                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query historical designs from PostgreSQL
        
        Args:
            filters: Query filters (network_type, status, date_range, etc.)
            limit: Maximum results
        
        Returns:
            List of historical designs
        """
        if not self.pg_pool:
            logger.error("PostgreSQL not connected")
            return []
        
        try:
            # Build query
            query = """
                SELECT 
                    design_id,
                    name,
                    description,
                    network_type,
                    topology_type,
                    status,
                    validation_score,
                    component_count,
                    created_at,
                    validated_at,
                    design_data
                FROM network_designs
                WHERE 1=1
            """
            
            params = []
            param_count = 1
            
            # Add filters
            if 'network_type' in filters:
                query += f" AND network_type = ${param_count}"
                params.append(filters['network_type'])
                param_count += 1
            
            if 'status' in filters:
                query += f" AND status = ${param_count}"
                params.append(filters['status'])
                param_count += 1
            
            if 'min_validation_score' in filters:
                query += f" AND validation_score >= ${param_count}"
                params.append(filters['min_validation_score'])
                param_count += 1
            
            if 'date_from' in filters:
                query += f" AND created_at >= ${param_count}"
                params.append(filters['date_from'])
                param_count += 1
            
            query += f" ORDER BY validation_score DESC, created_at DESC LIMIT ${param_count}"
            params.append(limit)
            
            # Execute query
            async with self.pg_pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                
                results = []
                for row in rows:
                    results.append(dict(row))
                
                logger.info(f"Retrieved {len(results)} historical designs from PostgreSQL")
                return results
                
        except Exception as e:
            logger.error(f"Failed to query PostgreSQL: {e}")
            return []
    
    async def query_historical_designs_mongo(self,
                                            database: str,
                                            collection: str,
                                            filters: Dict[str, Any],
                                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query historical designs from MongoDB
        
        Args:
            database: Database name
            collection: Collection name
            filters: Query filters
            limit: Maximum results
        
        Returns:
            List of historical designs
        """
        if not self.mongo_client:
            logger.error("MongoDB not connected")
            return []
        
        try:
            db = self.mongo_client[database]
            coll = db[collection]
            
            # Build query
            query = {}
            
            if 'network_type' in filters:
                query['network_type'] = filters['network_type']
            
            if 'status' in filters:
                query['status'] = filters['status']
            
            if 'min_validation_score' in filters:
                query['validation_score'] = {'$gte': filters['min_validation_score']}
            
            if 'date_from' in filters:
                query['created_at'] = {'$gte': filters['date_from']}
            
            # Execute query
            cursor = coll.find(query).sort([
                ('validation_score', -1),
                ('created_at', -1)
            ]).limit(limit)
            
            results = []
            async for doc in cursor:
                # Remove MongoDB _id
                doc.pop('_id', None)
                results.append(doc)
            
            logger.info(f"Retrieved {len(results)} historical designs from MongoDB")
            return results
            
        except Exception as e:
            logger.error(f"Failed to query MongoDB: {e}")
            return []
    
    def query_historical_designs_oracle(self,
                                       filters: Dict[str, Any],
                                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query historical designs from Oracle
        
        Args:
            filters: Query filters
            limit: Maximum results
        
        Returns:
            List of historical designs
        """
        if not self.oracle_pool:
            logger.error("Oracle not connected")
            return []
        
        try:
            with self.oracle_pool.acquire() as conn:
                cursor = conn.cursor()
                
                # Build query
                query = """
                    SELECT 
                        design_id,
                        name,
                        description,
                        network_type,
                        topology_type,
                        status,
                        validation_score,
                        component_count,
                        created_at,
                        validated_at,
                        design_data
                    FROM network_designs
                    WHERE 1=1
                """
                
                params = {}
                
                # Add filters
                if 'network_type' in filters:
                    query += " AND network_type = :network_type"
                    params['network_type'] = filters['network_type']
                
                if 'status' in filters:
                    query += " AND status = :status"
                    params['status'] = filters['status']
                
                if 'min_validation_score' in filters:
                    query += " AND validation_score >= :min_score"
                    params['min_score'] = filters['min_validation_score']
                
                query += " ORDER BY validation_score DESC, created_at DESC FETCH FIRST :limit ROWS ONLY"
                params['limit'] = limit
                
                # Execute query
                cursor.execute(query, params)
                
                # Fetch results
                columns = [col[0] for col in cursor.description]
                results = []
                
                for row in cursor:
                    results.append(dict(zip(columns, row)))
                
                logger.info(f"Retrieved {len(results)} historical designs from Oracle")
                return results
                
        except Exception as e:
            logger.error(f"Failed to query Oracle: {e}")
            return []
    
    async def get_design_statistics(self, source: str = "postgresql") -> Dict[str, Any]:
        """
        Get statistics about historical designs
        
        Args:
            source: Database source (postgresql, mongodb, oracle)
        
        Returns:
            Statistics dictionary
        """
        try:
            if source == "postgresql" and self.pg_pool:
                async with self.pg_pool.acquire() as conn:
                    stats = await conn.fetchrow("""
                        SELECT 
                            COUNT(*) as total_designs,
                            COUNT(DISTINCT network_type) as network_types,
                            AVG(validation_score) as avg_validation_score,
                            MAX(validation_score) as max_validation_score,
                            COUNT(CASE WHEN status = 'validated' THEN 1 END) as validated_count
                        FROM network_designs
                    """)
                    
                    return dict(stats)
            
            elif source == "mongodb" and self.mongo_client:
                # Implement MongoDB aggregation
                pass
            
            elif source == "oracle" and self.oracle_pool:
                # Implement Oracle query
                pass
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    async def close(self):
        """Close all database connections"""
        try:
            if self.pg_pool:
                await self.pg_pool.close()
                logger.info("Closed PostgreSQL connection")
            
            if self.mongo_client:
                self.mongo_client.close()
                logger.info("Closed MongoDB connection")
            
            if self.oracle_pool:
                self.oracle_pool.close()
                logger.info("Closed Oracle connection")
                
        except Exception as e:
            logger.error(f"Error closing connections: {e}")


# Dependency injection
_external_db_connector: Optional[ExternalDatabaseConnector] = None


def get_external_db_connector() -> ExternalDatabaseConnector:
    """Get external database connector for dependency injection"""
    global _external_db_connector
    if _external_db_connector is None:
        _external_db_connector = ExternalDatabaseConnector()
    return _external_db_connector
