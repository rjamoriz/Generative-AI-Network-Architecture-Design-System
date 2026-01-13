"""
Design Repository
Database operations for network designs
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.network_design import NetworkDesign, DesignStatus, NetworkType, TopologyType

logger = logging.getLogger(__name__)


class DesignRepository:
    """Repository for network design CRUD operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize design repository
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.collection = db.designs
        
        logger.info("Design repository initialized")
    
    async def create_design(self, design: NetworkDesign) -> str:
        """
        Create new design in database
        
        Args:
            design: Network design to create
        
        Returns:
            Design ID
        """
        try:
            # Convert to dict
            design_dict = design.model_dump(mode='json')
            
            # Add metadata
            design_dict['created_at'] = datetime.utcnow()
            design_dict['updated_at'] = datetime.utcnow()
            
            # Insert into database
            result = await self.collection.insert_one(design_dict)
            
            logger.info(f"Created design: {design.design_id}")
            return design.design_id
            
        except Exception as e:
            logger.error(f"Failed to create design: {e}")
            raise
    
    async def get_design(self, design_id: str) -> Optional[NetworkDesign]:
        """
        Retrieve design by ID
        
        Args:
            design_id: Design identifier
        
        Returns:
            NetworkDesign or None
        """
        try:
            design_dict = await self.collection.find_one({"design_id": design_id})
            
            if not design_dict:
                return None
            
            # Remove MongoDB _id
            design_dict.pop('_id', None)
            
            # Convert to model
            design = NetworkDesign(**design_dict)
            
            logger.info(f"Retrieved design: {design_id}")
            return design
            
        except Exception as e:
            logger.error(f"Failed to retrieve design {design_id}: {e}")
            return None
    
    async def update_design(self, design: NetworkDesign) -> bool:
        """
        Update existing design
        
        Args:
            design: Updated network design
        
        Returns:
            True if successful
        """
        try:
            design_dict = design.model_dump(mode='json')
            design_dict['updated_at'] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"design_id": design.design_id},
                {"$set": design_dict}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated design: {design.design_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update design: {e}")
            return False
    
    async def delete_design(self, design_id: str) -> bool:
        """
        Delete design
        
        Args:
            design_id: Design identifier
        
        Returns:
            True if successful
        """
        try:
            result = await self.collection.delete_one({"design_id": design_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted design: {design_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete design: {e}")
            return False
    
    async def list_designs(self,
                          skip: int = 0,
                          limit: int = 100,
                          status: Optional[DesignStatus] = None,
                          network_type: Optional[NetworkType] = None) -> List[NetworkDesign]:
        """
        List designs with filtering
        
        Args:
            skip: Number of designs to skip
            limit: Maximum number to return
            status: Filter by status
            network_type: Filter by network type
        
        Returns:
            List of designs
        """
        try:
            # Build filter
            filter_dict = {}
            if status:
                filter_dict['status'] = status.value
            if network_type:
                filter_dict['network_type'] = network_type.value
            
            # Query database
            cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
            designs = []
            
            async for design_dict in cursor:
                design_dict.pop('_id', None)
                try:
                    design = NetworkDesign(**design_dict)
                    designs.append(design)
                except Exception as e:
                    logger.warning(f"Failed to parse design: {e}")
            
            logger.info(f"Listed {len(designs)} designs")
            return designs
            
        except Exception as e:
            logger.error(f"Failed to list designs: {e}")
            return []
    
    async def search_designs(self,
                           query: str,
                           limit: int = 10) -> List[NetworkDesign]:
        """
        Search designs by text
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            List of matching designs
        """
        try:
            # Text search on name and description
            filter_dict = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = self.collection.find(filter_dict).limit(limit)
            designs = []
            
            async for design_dict in cursor:
                design_dict.pop('_id', None)
                try:
                    design = NetworkDesign(**design_dict)
                    designs.append(design)
                except Exception as e:
                    logger.warning(f"Failed to parse design: {e}")
            
            logger.info(f"Search '{query}' returned {len(designs)} results")
            return designs
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def get_design_count(self,
                              status: Optional[DesignStatus] = None,
                              network_type: Optional[NetworkType] = None) -> int:
        """
        Get count of designs
        
        Args:
            status: Filter by status
            network_type: Filter by network type
        
        Returns:
            Count of designs
        """
        try:
            filter_dict = {}
            if status:
                filter_dict['status'] = status.value
            if network_type:
                filter_dict['network_type'] = network_type.value
            
            count = await self.collection.count_documents(filter_dict)
            return count
            
        except Exception as e:
            logger.error(f"Failed to count designs: {e}")
            return 0
    
    async def get_designs_by_requirements(self, requirements_id: str) -> List[NetworkDesign]:
        """
        Get all designs for a requirements ID
        
        Args:
            requirements_id: Requirements identifier
        
        Returns:
            List of designs
        """
        try:
            cursor = self.collection.find({"requirements_id": requirements_id})
            designs = []
            
            async for design_dict in cursor:
                design_dict.pop('_id', None)
                try:
                    design = NetworkDesign(**design_dict)
                    designs.append(design)
                except Exception as e:
                    logger.warning(f"Failed to parse design: {e}")
            
            return designs
            
        except Exception as e:
            logger.error(f"Failed to get designs by requirements: {e}")
            return []
    
    async def update_design_status(self, design_id: str, status: DesignStatus) -> bool:
        """
        Update design status
        
        Args:
            design_id: Design identifier
            status: New status
        
        Returns:
            True if successful
        """
        try:
            result = await self.collection.update_one(
                {"design_id": design_id},
                {
                    "$set": {
                        "status": status.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated design {design_id} status to {status.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update design status: {e}")
            return False
    
    async def create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Index on design_id
            await self.collection.create_index("design_id", unique=True)
            
            # Index on status
            await self.collection.create_index("status")
            
            # Index on network_type
            await self.collection.create_index("network_type")
            
            # Index on requirements_id
            await self.collection.create_index("requirements_id")
            
            # Text index for search
            await self.collection.create_index([
                ("name", "text"),
                ("description", "text")
            ])
            
            # Index on created_at for sorting
            await self.collection.create_index("created_at")
            
            logger.info("Database indexes created")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")


# Dependency injection
def get_design_repository(db: AsyncIOMotorDatabase) -> DesignRepository:
    """Get design repository for dependency injection"""
    return DesignRepository(db)
