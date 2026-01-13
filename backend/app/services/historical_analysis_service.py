"""
Historical Analysis Service
Analyzes historical network designs to provide insights and recommendations
"""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict

from app.integrations.external_db_connector import ExternalDatabaseConnector
from app.models.network_design import NetworkType, TopologyType, SecurityLevel
from app.models.requirements import NetworkRequirements

logger = logging.getLogger(__name__)


class HistoricalAnalysisService:
    """
    Service for analyzing historical network designs
    Provides insights, patterns, and recommendations based on past validated designs
    """
    
    def __init__(self, db_connector: ExternalDatabaseConnector):
        """
        Initialize historical analysis service
        
        Args:
            db_connector: External database connector
        """
        self.db_connector = db_connector
        
        logger.info("Historical analysis service initialized")
    
    async def find_similar_validated_designs(self,
                                            requirements: NetworkRequirements,
                                            min_validation_score: float = 0.85,
                                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar validated designs from historical data
        
        Args:
            requirements: Network requirements to match
            min_validation_score: Minimum validation score
            limit: Maximum results
        
        Returns:
            List of similar validated designs
        """
        try:
            # Build filters based on requirements
            filters = {
                'network_type': requirements.network_type.value,
                'status': 'validated',
                'min_validation_score': min_validation_score
            }
            
            # Query from PostgreSQL (primary source)
            designs = await self.db_connector.query_historical_designs_pg(filters, limit)
            
            # If not enough results, try MongoDB
            if len(designs) < limit and self.db_connector.mongo_client:
                mongo_designs = await self.db_connector.query_historical_designs_mongo(
                    database='network_designs',
                    collection='validated_designs',
                    filters=filters,
                    limit=limit - len(designs)
                )
                designs.extend(mongo_designs)
            
            # Rank by similarity to requirements
            ranked_designs = self._rank_by_similarity(designs, requirements)
            
            logger.info(f"Found {len(ranked_designs)} similar validated designs")
            return ranked_designs[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar designs: {e}")
            return []
    
    def _rank_by_similarity(self,
                           designs: List[Dict[str, Any]],
                           requirements: NetworkRequirements) -> List[Dict[str, Any]]:
        """
        Rank designs by similarity to requirements
        
        Args:
            designs: List of designs
            requirements: Target requirements
        
        Returns:
            Ranked list of designs
        """
        scored_designs = []
        
        for design in designs:
            similarity_score = 0.0
            
            # Network type match (40%)
            if design.get('network_type') == requirements.network_type.value:
                similarity_score += 0.4
            
            # Topology match (20%)
            if requirements.topology_preference:
                if design.get('topology_type') == requirements.topology_preference.value:
                    similarity_score += 0.2
            
            # Scale similarity (20%)
            if requirements.scale and 'component_count' in design:
                # Rough scale matching
                target_scale = requirements.scale.devices
                design_scale = design.get('component_count', 0) * 50  # Estimate
                
                if target_scale > 0:
                    scale_ratio = min(design_scale, target_scale) / max(design_scale, target_scale)
                    similarity_score += 0.2 * scale_ratio
            
            # Security level match (10%)
            if design.get('security_level') == requirements.security_level.value:
                similarity_score += 0.1
            
            # Validation score bonus (10%)
            validation_score = design.get('validation_score', 0)
            similarity_score += 0.1 * validation_score
            
            design['similarity_score'] = similarity_score
            scored_designs.append(design)
        
        # Sort by similarity score
        scored_designs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return scored_designs
    
    async def analyze_design_patterns(self,
                                     network_type: NetworkType,
                                     days_back: int = 365) -> Dict[str, Any]:
        """
        Analyze patterns in historical designs
        
        Args:
            network_type: Network type to analyze
            days_back: Number of days to look back
        
        Returns:
            Pattern analysis results
        """
        try:
            date_from = datetime.utcnow() - timedelta(days=days_back)
            
            filters = {
                'network_type': network_type.value,
                'status': 'validated',
                'date_from': date_from,
                'min_validation_score': 0.8
            }
            
            # Get historical designs
            designs = await self.db_connector.query_historical_designs_pg(filters, limit=500)
            
            if not designs:
                return {"message": "No historical data available"}
            
            # Analyze patterns
            patterns = {
                'total_designs': len(designs),
                'network_type': network_type.value,
                'topology_distribution': defaultdict(int),
                'avg_validation_score': 0.0,
                'avg_component_count': 0.0,
                'common_features': [],
                'success_factors': []
            }
            
            total_validation_score = 0.0
            total_components = 0
            
            for design in designs:
                # Topology distribution
                topology = design.get('topology_type', 'unknown')
                patterns['topology_distribution'][topology] += 1
                
                # Averages
                total_validation_score += design.get('validation_score', 0)
                total_components += design.get('component_count', 0)
            
            patterns['avg_validation_score'] = total_validation_score / len(designs)
            patterns['avg_component_count'] = total_components / len(designs)
            
            # Convert defaultdict to dict
            patterns['topology_distribution'] = dict(patterns['topology_distribution'])
            
            # Identify most successful topology
            if patterns['topology_distribution']:
                most_common_topology = max(
                    patterns['topology_distribution'].items(),
                    key=lambda x: x[1]
                )[0]
                patterns['recommended_topology'] = most_common_topology
            
            logger.info(f"Analyzed {len(designs)} designs for patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze patterns: {e}")
            return {}
    
    async def get_best_practices(self,
                                network_type: NetworkType,
                                security_level: SecurityLevel) -> Dict[str, Any]:
        """
        Extract best practices from highly validated designs
        
        Args:
            network_type: Network type
            security_level: Security level
        
        Returns:
            Best practices and recommendations
        """
        try:
            filters = {
                'network_type': network_type.value,
                'status': 'validated',
                'min_validation_score': 0.95  # Only top-performing designs
            }
            
            designs = await self.db_connector.query_historical_designs_pg(filters, limit=50)
            
            if not designs:
                return {"message": "No best practices data available"}
            
            best_practices = {
                'network_type': network_type.value,
                'security_level': security_level.value,
                'sample_size': len(designs),
                'recommendations': [],
                'common_components': [],
                'typical_topology': None,
                'avg_validation_score': 0.0
            }
            
            # Analyze top designs
            topology_counts = defaultdict(int)
            total_score = 0.0
            
            for design in designs:
                topology_counts[design.get('topology_type', 'unknown')] += 1
                total_score += design.get('validation_score', 0)
            
            best_practices['avg_validation_score'] = total_score / len(designs)
            
            # Most common topology in best designs
            if topology_counts:
                best_practices['typical_topology'] = max(
                    topology_counts.items(),
                    key=lambda x: x[1]
                )[0]
            
            # Generate recommendations
            best_practices['recommendations'] = [
                f"Use {best_practices['typical_topology']} topology for optimal results",
                f"Target validation score: {best_practices['avg_validation_score']:.2f}",
                f"Based on {len(designs)} highly validated designs"
            ]
            
            logger.info(f"Extracted best practices from {len(designs)} top designs")
            return best_practices
            
        except Exception as e:
            logger.error(f"Failed to get best practices: {e}")
            return {}
    
    async def get_validation_insights(self,
                                     network_type: NetworkType) -> Dict[str, Any]:
        """
        Get insights about validation patterns
        
        Args:
            network_type: Network type
        
        Returns:
            Validation insights
        """
        try:
            filters = {
                'network_type': network_type.value
            }
            
            designs = await self.db_connector.query_historical_designs_pg(filters, limit=1000)
            
            if not designs:
                return {"message": "No validation data available"}
            
            insights = {
                'network_type': network_type.value,
                'total_designs': len(designs),
                'validation_rate': 0.0,
                'avg_score': 0.0,
                'common_issues': [],
                'success_rate_by_topology': {}
            }
            
            validated_count = 0
            total_score = 0.0
            topology_stats = defaultdict(lambda: {'count': 0, 'validated': 0, 'total_score': 0.0})
            
            for design in designs:
                if design.get('status') == 'validated':
                    validated_count += 1
                
                score = design.get('validation_score', 0)
                total_score += score
                
                topology = design.get('topology_type', 'unknown')
                topology_stats[topology]['count'] += 1
                if design.get('status') == 'validated':
                    topology_stats[topology]['validated'] += 1
                topology_stats[topology]['total_score'] += score
            
            insights['validation_rate'] = validated_count / len(designs) if designs else 0
            insights['avg_score'] = total_score / len(designs) if designs else 0
            
            # Calculate success rate by topology
            for topology, stats in topology_stats.items():
                insights['success_rate_by_topology'][topology] = {
                    'validation_rate': stats['validated'] / stats['count'] if stats['count'] > 0 else 0,
                    'avg_score': stats['total_score'] / stats['count'] if stats['count'] > 0 else 0,
                    'sample_size': stats['count']
                }
            
            logger.info(f"Generated validation insights from {len(designs)} designs")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get validation insights: {e}")
            return {}
    
    async def build_historical_context(self,
                                      requirements: NetworkRequirements,
                                      max_designs: int = 5) -> str:
        """
        Build context string from historical designs for LLM prompts
        
        Args:
            requirements: Network requirements
            max_designs: Maximum designs to include
        
        Returns:
            Formatted context string
        """
        try:
            # Get similar validated designs
            similar_designs = await self.find_similar_validated_designs(
                requirements,
                min_validation_score=0.85,
                limit=max_designs
            )
            
            if not similar_designs:
                return "No historical design data available for this network type."
            
            # Build context string
            context = f"Historical Validated Designs ({len(similar_designs)} examples):\n\n"
            
            for i, design in enumerate(similar_designs, 1):
                context += f"{i}. {design.get('name', 'Unnamed Design')}\n"
                context += f"   - Network Type: {design.get('network_type', 'Unknown')}\n"
                context += f"   - Topology: {design.get('topology_type', 'Unknown')}\n"
                context += f"   - Validation Score: {design.get('validation_score', 0):.2f}\n"
                context += f"   - Components: {design.get('component_count', 0)}\n"
                context += f"   - Similarity: {design.get('similarity_score', 0):.2f}\n"
                
                if 'description' in design:
                    context += f"   - Description: {design['description'][:200]}\n"
                
                context += "\n"
            
            # Add pattern analysis
            patterns = await self.analyze_design_patterns(requirements.network_type, days_back=180)
            
            if patterns and 'recommended_topology' in patterns:
                context += f"Pattern Analysis:\n"
                context += f"- Most successful topology: {patterns['recommended_topology']}\n"
                context += f"- Average validation score: {patterns.get('avg_validation_score', 0):.2f}\n"
                context += f"- Based on {patterns.get('total_designs', 0)} validated designs\n"
            
            logger.info(f"Built historical context with {len(similar_designs)} designs")
            return context
            
        except Exception as e:
            logger.error(f"Failed to build historical context: {e}")
            return "Error retrieving historical design data."


# Dependency injection
def get_historical_analysis_service(
    db_connector: ExternalDatabaseConnector
) -> HistoricalAnalysisService:
    """Get historical analysis service for dependency injection"""
    return HistoricalAnalysisService(db_connector)
