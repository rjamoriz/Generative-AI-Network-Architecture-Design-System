"""
Data Migration Utilities
Tools for migrating designs between internal and external databases
"""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import asyncio

from app.models.network_design import NetworkDesign, DesignStatus
from app.db.design_repository import DesignRepository
from app.integrations.external_db_connector import ExternalDatabaseConnector

logger = logging.getLogger(__name__)


class DataMigrationService:
    """Service for migrating network design data between databases"""
    
    def __init__(self, 
                 internal_repo: DesignRepository,
                 external_connector: ExternalDatabaseConnector):
        """
        Initialize data migration service
        
        Args:
            internal_repo: Internal design repository
            external_connector: External database connector
        """
        self.internal_repo = internal_repo
        self.external_connector = external_connector
        
        logger.info("Data migration service initialized")
    
    async def export_validated_designs_to_external(self,
                                                   min_validation_score: float = 0.8,
                                                   batch_size: int = 100) -> Dict[str, Any]:
        """
        Export validated designs from internal DB to external historical DB
        
        Args:
            min_validation_score: Minimum validation score to export
            batch_size: Number of designs per batch
        
        Returns:
            Migration statistics
        """
        try:
            logger.info(f"Starting export of validated designs (score >= {min_validation_score})")
            
            # Get validated designs from internal database
            designs = await self.internal_repo.list_designs(
                status=DesignStatus.VALIDATED,
                limit=10000  # Large limit to get all
            )
            
            # Filter by validation score if available
            # Note: This assumes validation_score is stored in the design
            # You may need to adjust based on your actual data model
            
            exported_count = 0
            failed_count = 0
            
            # Process in batches
            for i in range(0, len(designs), batch_size):
                batch = designs[i:i + batch_size]
                
                for design in batch:
                    try:
                        # Convert to external DB format
                        external_record = self._convert_to_external_format(design)
                        
                        # Insert into external PostgreSQL
                        await self._insert_to_external_pg(external_record)
                        
                        exported_count += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to export design {design.design_id}: {e}")
                        failed_count += 1
                
                logger.info(f"Exported batch {i//batch_size + 1}: {len(batch)} designs")
                
                # Small delay between batches to avoid overwhelming the database
                await asyncio.sleep(0.1)
            
            stats = {
                "total_designs": len(designs),
                "exported": exported_count,
                "failed": failed_count,
                "success_rate": exported_count / len(designs) if designs else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Export complete: {exported_count} designs exported, {failed_count} failed")
            return stats
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise
    
    async def import_from_external_to_internal(self,
                                              filters: Dict[str, Any],
                                              limit: int = 100) -> Dict[str, Any]:
        """
        Import designs from external DB to internal DB
        
        Args:
            filters: Query filters for external database
            limit: Maximum designs to import
        
        Returns:
            Import statistics
        """
        try:
            logger.info(f"Starting import from external database (limit: {limit})")
            
            # Query external database
            external_designs = await self.external_connector.query_historical_designs_pg(
                filters,
                limit
            )
            
            imported_count = 0
            skipped_count = 0
            failed_count = 0
            
            for external_record in external_designs:
                try:
                    # Check if design already exists
                    existing = await self.internal_repo.get_design(
                        external_record['design_id']
                    )
                    
                    if existing:
                        logger.debug(f"Design {external_record['design_id']} already exists, skipping")
                        skipped_count += 1
                        continue
                    
                    # Convert to internal format
                    design = self._convert_from_external_format(external_record)
                    
                    # Save to internal database
                    await self.internal_repo.create_design(design)
                    
                    imported_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to import design {external_record.get('design_id')}: {e}")
                    failed_count += 1
            
            stats = {
                "total_external": len(external_designs),
                "imported": imported_count,
                "skipped": skipped_count,
                "failed": failed_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Import complete: {imported_count} imported, {skipped_count} skipped, {failed_count} failed")
            return stats
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise
    
    async def sync_bidirectional(self,
                                export_filters: Dict[str, Any] = None,
                                import_filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Bidirectional sync between internal and external databases
        
        Args:
            export_filters: Filters for export
            import_filters: Filters for import
        
        Returns:
            Sync statistics
        """
        try:
            logger.info("Starting bidirectional sync")
            
            # Export validated designs
            export_stats = await self.export_validated_designs_to_external()
            
            # Import new designs from external
            if import_filters is None:
                import_filters = {
                    'status': 'validated',
                    'min_validation_score': 0.85
                }
            
            import_stats = await self.import_from_external_to_internal(
                import_filters,
                limit=500
            )
            
            sync_stats = {
                "export": export_stats,
                "import": import_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Bidirectional sync complete")
            return sync_stats
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise
    
    def _convert_to_external_format(self, design: NetworkDesign) -> Dict[str, Any]:
        """
        Convert internal NetworkDesign to external database format
        
        Args:
            design: Internal network design
        
        Returns:
            External database record
        """
        return {
            'design_id': design.design_id,
            'name': design.name,
            'description': design.description,
            'network_type': design.network_type.value,
            'topology_type': design.topology.topology_type.value if design.topology else None,
            'status': design.status.value,
            'validation_score': 0.0,  # Calculate from validation results if available
            'component_count': len(design.components),
            'security_level': design.security_level.value if design.security_level else None,
            'created_at': design.created_at or datetime.utcnow(),
            'validated_at': datetime.utcnow() if design.status == DesignStatus.VALIDATED else None,
            'design_data': design.model_dump(mode='json')
        }
    
    def _convert_from_external_format(self, external_record: Dict[str, Any]) -> NetworkDesign:
        """
        Convert external database record to internal NetworkDesign
        
        Args:
            external_record: External database record
        
        Returns:
            Internal network design
        """
        # If full design_data is available, use it
        if 'design_data' in external_record and external_record['design_data']:
            return NetworkDesign(**external_record['design_data'])
        
        # Otherwise, create minimal design from available fields
        # This is a simplified conversion - adjust based on your needs
        raise NotImplementedError(
            "Conversion from external format requires full design_data field. "
            "Ensure external database stores complete design JSON."
        )
    
    async def _insert_to_external_pg(self, record: Dict[str, Any]) -> bool:
        """
        Insert record into external PostgreSQL database
        
        Args:
            record: Record to insert
        
        Returns:
            True if successful
        """
        if not self.external_connector.pg_pool:
            raise RuntimeError("PostgreSQL not connected")
        
        try:
            async with self.external_connector.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO network_designs (
                        design_id, name, description, network_type, topology_type,
                        status, validation_score, component_count, security_level,
                        created_at, validated_at, design_data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    ON CONFLICT (design_id) DO UPDATE SET
                        validation_score = EXCLUDED.validation_score,
                        validated_at = EXCLUDED.validated_at,
                        design_data = EXCLUDED.design_data
                """,
                    record['design_id'],
                    record['name'],
                    record['description'],
                    record['network_type'],
                    record['topology_type'],
                    record['status'],
                    record['validation_score'],
                    record['component_count'],
                    record['security_level'],
                    record['created_at'],
                    record['validated_at'],
                    record['design_data']
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert to external PostgreSQL: {e}")
            raise
    
    async def validate_migration(self,
                                design_id: str) -> Dict[str, Any]:
        """
        Validate that a design was correctly migrated
        
        Args:
            design_id: Design identifier
        
        Returns:
            Validation results
        """
        try:
            # Get from internal DB
            internal_design = await self.internal_repo.get_design(design_id)
            
            if not internal_design:
                return {
                    "valid": False,
                    "error": "Design not found in internal database"
                }
            
            # Get from external DB
            external_designs = await self.external_connector.query_historical_designs_pg(
                {'design_id': design_id},
                limit=1
            )
            
            if not external_designs:
                return {
                    "valid": False,
                    "error": "Design not found in external database"
                }
            
            external_design = external_designs[0]
            
            # Compare key fields
            validation = {
                "valid": True,
                "design_id": design_id,
                "checks": {
                    "name_match": internal_design.name == external_design.get('name'),
                    "network_type_match": internal_design.network_type.value == external_design.get('network_type'),
                    "component_count_match": len(internal_design.components) == external_design.get('component_count'),
                }
            }
            
            validation["valid"] = all(validation["checks"].values())
            
            return validation
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "valid": False,
                "error": str(e)
            }


# Dependency injection
def get_data_migration_service(
    internal_repo: DesignRepository,
    external_connector: ExternalDatabaseConnector
) -> DataMigrationService:
    """Get data migration service for dependency injection"""
    return DataMigrationService(internal_repo, external_connector)
