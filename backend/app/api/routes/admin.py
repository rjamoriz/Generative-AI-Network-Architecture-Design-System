"""
Admin API Routes
Endpoints for system administration and rule management
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.validation.rule_registry import RuleRegistry, get_rule_registry
from app.validation.rule_base import RuleCategory, RuleSeverity

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/rules/statistics", response_model=Dict[str, Any])
async def get_rule_statistics(
    registry: RuleRegistry = Depends(get_rule_registry)
) -> Dict[str, Any]:
    """
    Get validation rule statistics
    
    Returns statistics about loaded rules, categories, and severity distribution
    """
    try:
        stats = registry.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get rule statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/rules", response_model=List[Dict[str, Any]])
async def list_rules(
    category: str = None,
    tag: str = None,
    enabled_only: bool = False,
    registry: RuleRegistry = Depends(get_rule_registry)
) -> List[Dict[str, Any]]:
    """
    List validation rules with optional filtering
    
    Args:
        category: Filter by category (capacity, topology, protocol, security, compliance)
        tag: Filter by tag
        enabled_only: Only return enabled rules
    
    Returns:
        List of rule metadata
    """
    try:
        # Get rules based on filters
        if category:
            try:
                cat = RuleCategory(category.lower())
                rules = registry.get_rules_by_category(cat)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category: {category}"
                )
        elif tag:
            rules = registry.get_rules_by_tag(tag)
        elif enabled_only:
            rules = registry.get_enabled_rules()
        else:
            rules = registry.get_all_rules()
        
        # Convert to dict
        rule_list = []
        for rule in rules:
            metadata = rule.get_metadata()
            rule_list.append({
                "rule_id": rule.get_rule_id(),
                "name": metadata.get("name"),
                "description": metadata.get("description"),
                "category": metadata.get("category").value if metadata.get("category") else None,
                "severity": metadata.get("severity").value if metadata.get("severity") else None,
                "tags": metadata.get("tags", []),
                "enabled": rule.is_enabled()
            })
        
        return rule_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rules: {str(e)}"
        )


@router.post("/rules/{rule_id}/enable")
async def enable_rule(
    rule_id: str,
    registry: RuleRegistry = Depends(get_rule_registry)
) -> Dict[str, Any]:
    """
    Enable a validation rule
    
    Args:
        rule_id: Rule identifier
    
    Returns:
        Success message
    """
    try:
        success = registry.enable_rule(rule_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule not found: {rule_id}"
            )
        
        return {
            "message": f"Rule {rule_id} enabled",
            "rule_id": rule_id,
            "enabled": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable rule: {str(e)}"
        )


@router.post("/rules/{rule_id}/disable")
async def disable_rule(
    rule_id: str,
    registry: RuleRegistry = Depends(get_rule_registry)
) -> Dict[str, Any]:
    """
    Disable a validation rule
    
    Args:
        rule_id: Rule identifier
    
    Returns:
        Success message
    """
    try:
        success = registry.disable_rule(rule_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule not found: {rule_id}"
            )
        
        return {
            "message": f"Rule {rule_id} disabled",
            "rule_id": rule_id,
            "enabled": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable rule: {str(e)}"
        )


@router.post("/rules/category/{category}/enable")
async def enable_category(
    category: str,
    registry: RuleRegistry = Depends(get_rule_registry)
) -> Dict[str, Any]:
    """
    Enable all rules in a category
    
    Args:
        category: Category name
    
    Returns:
        Success message with count
    """
    try:
        try:
            cat = RuleCategory(category.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}"
            )
        
        count = registry.enable_category(cat)
        
        return {
            "message": f"Enabled {count} rules in category {category}",
            "category": category,
            "rules_enabled": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable category: {str(e)}"
        )


@router.post("/rules/category/{category}/disable")
async def disable_category(
    category: str,
    registry: RuleRegistry = Depends(get_rule_registry)
) -> Dict[str, Any]:
    """
    Disable all rules in a category
    
    Args:
        category: Category name
    
    Returns:
        Success message with count
    """
    try:
        try:
            cat = RuleCategory(category.lower())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}"
            )
        
        count = registry.disable_category(cat)
        
        return {
            "message": f"Disabled {count} rules in category {category}",
            "category": category,
            "rules_disabled": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable category: {str(e)}"
        )


@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(
    registry: RuleRegistry = Depends(get_rule_registry)
) -> Dict[str, Any]:
    """
    Detailed health check with component status
    
    Returns:
        Detailed system health information
    """
    try:
        stats = registry.get_statistics()
        
        return {
            "status": "healthy",
            "timestamp": str(datetime.utcnow()),
            "components": {
                "validation_engine": {
                    "status": "operational",
                    "total_rules": stats["total_rules"],
                    "enabled_rules": stats["enabled_rules"]
                },
                "rule_registry": {
                    "status": "operational",
                    "categories": len(stats["categories"])
                }
            },
            "metrics": {
                "rules_by_category": stats["categories"],
                "rules_by_severity": stats["severity_distribution"]
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "timestamp": str(datetime.utcnow()),
            "error": str(e)
        }


from datetime import datetime
