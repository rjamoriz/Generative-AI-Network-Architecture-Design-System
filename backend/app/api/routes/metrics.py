"""
Metrics and Monitoring API Routes
Endpoints for system metrics, health checks, and monitoring
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends
import logging
import psutil
import time
from datetime import datetime

from app.validation.rule_registry import RuleRegistry, get_rule_registry

logger = logging.getLogger(__name__)

router = APIRouter()

# Track application start time
_app_start_time = time.time()

# Simple request counter (in production, use Prometheus)
_request_counts = {
    "total": 0,
    "success": 0,
    "error": 0
}


@router.get("/health/detailed")
async def detailed_health_check(
    registry: RuleRegistry = Depends(get_rule_registry)
) -> Dict[str, Any]:
    """
    Detailed health check with component status
    
    Returns comprehensive health information about all system components
    """
    try:
        # Get rule statistics
        rule_stats = registry.get_statistics()
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": int(time.time() - _app_start_time),
            "components": {
                "validation_engine": {
                    "status": "operational",
                    "total_rules": rule_stats["total_rules"],
                    "enabled_rules": rule_stats["enabled_rules"]
                },
                "rule_registry": {
                    "status": "operational",
                    "categories": len(rule_stats["categories"])
                },
                "api": {
                    "status": "operational",
                    "total_requests": _request_counts["total"],
                    "success_rate": _request_counts["success"] / max(_request_counts["total"], 1)
                }
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 * 1024 * 1024)
            },
            "metrics": {
                "rules_by_category": rule_stats["categories"],
                "rules_by_severity": rule_stats["severity_distribution"]
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/metrics/system")
async def get_system_metrics() -> Dict[str, Any]:
    """
    Get system resource metrics
    
    Returns CPU, memory, disk, and network statistics
    """
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics (if available)
        try:
            net_io = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except Exception:
            network_stats = None
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024),
                "used_mb": memory.used / (1024 * 1024),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "used_gb": disk.used / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024),
                "percent": disk.percent
            },
            "network": network_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/metrics/application")
async def get_application_metrics(
    registry: RuleRegistry = Depends(get_rule_registry)
) -> Dict[str, Any]:
    """
    Get application-specific metrics
    
    Returns validation engine statistics and API usage metrics
    """
    try:
        rule_stats = registry.get_statistics()
        
        uptime = int(time.time() - _app_start_time)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": {
                "seconds": uptime,
                "minutes": uptime // 60,
                "hours": uptime // 3600
            },
            "validation_engine": {
                "total_rules": rule_stats["total_rules"],
                "enabled_rules": rule_stats["enabled_rules"],
                "disabled_rules": rule_stats["total_rules"] - rule_stats["enabled_rules"],
                "categories": rule_stats["categories"],
                "severity_distribution": rule_stats["severity_distribution"]
            },
            "api": {
                "total_requests": _request_counts["total"],
                "successful_requests": _request_counts["success"],
                "failed_requests": _request_counts["error"],
                "success_rate": _request_counts["success"] / max(_request_counts["total"], 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get application metrics: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/metrics/prometheus")
async def get_prometheus_metrics(
    registry: RuleRegistry = Depends(get_rule_registry)
) -> str:
    """
    Get metrics in Prometheus format
    
    Returns metrics formatted for Prometheus scraping
    """
    try:
        rule_stats = registry.get_statistics()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        metrics = []
        
        # Application metrics
        metrics.append(f"# HELP app_uptime_seconds Application uptime in seconds")
        metrics.append(f"# TYPE app_uptime_seconds gauge")
        metrics.append(f"app_uptime_seconds {int(time.time() - _app_start_time)}")
        
        metrics.append(f"# HELP validation_rules_total Total number of validation rules")
        metrics.append(f"# TYPE validation_rules_total gauge")
        metrics.append(f"validation_rules_total {rule_stats['total_rules']}")
        
        metrics.append(f"# HELP validation_rules_enabled Number of enabled validation rules")
        metrics.append(f"# TYPE validation_rules_enabled gauge")
        metrics.append(f"validation_rules_enabled {rule_stats['enabled_rules']}")
        
        # Request metrics
        metrics.append(f"# HELP http_requests_total Total HTTP requests")
        metrics.append(f"# TYPE http_requests_total counter")
        metrics.append(f"http_requests_total {_request_counts['total']}")
        
        metrics.append(f"# HELP http_requests_success Successful HTTP requests")
        metrics.append(f"# TYPE http_requests_success counter")
        metrics.append(f"http_requests_success {_request_counts['success']}")
        
        # System metrics
        metrics.append(f"# HELP system_cpu_percent CPU usage percentage")
        metrics.append(f"# TYPE system_cpu_percent gauge")
        metrics.append(f"system_cpu_percent {cpu_percent}")
        
        metrics.append(f"# HELP system_memory_percent Memory usage percentage")
        metrics.append(f"# TYPE system_memory_percent gauge")
        metrics.append(f"system_memory_percent {memory.percent}")
        
        return "\n".join(metrics)
        
    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {e}")
        return f"# Error generating metrics: {str(e)}"


@router.post("/metrics/increment")
async def increment_request_counter(success: bool = True) -> Dict[str, Any]:
    """
    Increment request counter (internal use)
    
    Args:
        success: Whether the request was successful
    
    Returns:
        Updated counter values
    """
    _request_counts["total"] += 1
    if success:
        _request_counts["success"] += 1
    else:
        _request_counts["error"] += 1
    
    return {
        "total": _request_counts["total"],
        "success": _request_counts["success"],
        "error": _request_counts["error"]
    }


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Simple status endpoint
    
    Returns basic application status
    """
    return {
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - _app_start_time)
    }
