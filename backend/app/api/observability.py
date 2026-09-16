from fastapi import APIRouter, HTTPException
from app.services.observability_db import observability_db
from app.core.redis import redis_manager
from app.core.database import async_engine
from sqlalchemy import select, text, func
from app.models.chat import Chat, Message
from app.models.user import User
from app.models.memory import AgentExecution, Memory
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/observability/health")
async def observability_health():
    """Get observability system health"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "observability_db": "active",
            "runtime_state": "active",
            "redis": "connected" if redis_manager.redis else "disconnected"
        }
    }


@router.get("/observability/metrics")
async def get_metrics(
    metric_name: Optional[str] = None,
    hours: int = 24
):
    """Get metrics from PostgreSQL"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        metrics = await observability_db.get_metrics(
            metric_name=metric_name,
            start_time=start_time,
            limit=100
        )
        return {
            "metrics": metrics,
            "count": len(metrics),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")


@router.get("/observability/traces")
async def get_traces(
    trace_id: Optional[str] = None,
    service_name: Optional[str] = None,
    hours: int = 24
):
    """Get traces from PostgreSQL"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        traces = await observability_db.get_traces(
            trace_id=trace_id,
            service_name=service_name,
            start_time=start_time,
            limit=50
        )
        return {
            "traces": traces,
            "count": len(traces),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve traces: {str(e)}")


@router.get("/observability/logs")
async def get_logs(
    level: Optional[str] = None,
    hours: int = 24
):
    """Get logs from PostgreSQL"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        logs = await observability_db.get_logs(
            level=level,
            start_time=start_time,
            limit=100
        )
        return {
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")


@router.get("/observability/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        import psutil
        
        # Get current system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "percent": memory.percent,
                "available": memory.available,
                "total": memory.total,
                "used": memory.used
            },
            "disk": {
                "percent": disk.percent,
                "free": disk.free,
                "total": disk.total,
                "used": disk.used
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve performance metrics: {str(e)}")


@router.get("/observability/runtime-state")
async def get_runtime_state():
    """Get current runtime state from Redis"""
    try:
        # Get all Redis keys
        all_keys = await redis_manager.redis.keys("*")
        
        # Categorize keys
        key_categories = {
            "conversation": [],
            "agent_state": [],
            "response_cache": [],
            "tool_cache": [],
            "screenshot_cache": [],
            "workflow": [],
            "memory_queue": [],
            "other": []
        }
        
        for key in all_keys:
            if key.startswith("conversation:"):
                key_categories["conversation"].append(key)
            elif key.startswith("agent_state:"):
                key_categories["agent_state"].append(key)
            elif key.startswith("response:"):
                key_categories["response_cache"].append(key)
            elif key.startswith("tool:"):
                key_categories["tool_cache"].append(key)
            elif key.startswith("screenshot:"):
                key_categories["screenshot_cache"].append(key)
            elif key.startswith("workflow:"):
                key_categories["workflow"].append(key)
            elif key.startswith("memory_queue:"):
                key_categories["memory_queue"].append(key)
            else:
                key_categories["other"].append(key)
        
        # Get sample data from each category
        sample_data = {}
        for category, keys in key_categories.items():
            if keys:
                sample_key = keys[0]
                sample_value = await redis_manager.get(sample_key)
                sample_data[category] = {
                    "key": sample_key,
                    "value": sample_value,
                    "total_keys": len(keys)
                }
        
        return {
            "key_categories": {k: len(v) for k, v in key_categories.items()},
            "sample_data": sample_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve runtime state: {str(e)}")


@router.delete("/observability/logs")
async def delete_logs(
    before_days: Optional[int] = None,
    level: Optional[str] = None,
    logger_name: Optional[str] = None,
    delete_all: bool = False
):
    """Delete logs from PostgreSQL with optional filters"""
    try:
        if delete_all:
            # Delete all logs regardless of date
            deleted_count = await observability_db.delete_logs()
        else:
            before_date = None
            if before_days:
                before_date = datetime.utcnow() - timedelta(days=before_days)
            
            deleted_count = await observability_db.delete_logs(
                before_date=before_date,
                level=level,
                logger_name=logger_name
            )
        
        return {
            "message": f"Deleted {deleted_count} logs",
            "deleted_count": deleted_count,
            "filters": {
                "delete_all": delete_all,
                "before_days": before_days,
                "before_date": before_date.isoformat() if before_days else None,
                "level": level,
                "logger_name": logger_name
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete logs: {str(e)}")


@router.delete("/observability/traces")
async def delete_traces(
    before_days: Optional[int] = None,
    service_name: Optional[str] = None,
    delete_all: bool = False
):
    """Delete traces from PostgreSQL with optional filters"""
    try:
        if delete_all:
            # Delete all traces regardless of date
            deleted_count = await observability_db.delete_traces()
        else:
            before_date = None
            if before_days:
                before_date = datetime.utcnow() - timedelta(days=before_days)
            
            deleted_count = await observability_db.delete_traces(
                before_date=before_date,
                service_name=service_name
            )
        
        return {
            "message": f"Deleted {deleted_count} traces",
            "deleted_count": deleted_count,
            "filters": {
                "delete_all": delete_all,
                "before_days": before_days,
                "before_date": before_date.isoformat() if before_days else None,
                "service_name": service_name
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete traces: {str(e)}")


@router.delete("/observability/metrics")
async def delete_metrics(
    before_days: Optional[int] = None,
    metric_name: Optional[str] = None,
    delete_all: bool = False
):
    """Delete metrics from PostgreSQL with optional filters"""
    try:
        if delete_all:
            # Delete all metrics regardless of date
            deleted_count = await observability_db.delete_metrics()
        else:
            before_date = None
            if before_days:
                before_date = datetime.utcnow() - timedelta(days=before_days)
            
            deleted_count = await observability_db.delete_metrics(
                before_date=before_date,
                metric_name=metric_name
            )
        
        return {
            "message": f"Deleted {deleted_count} metrics",
            "deleted_count": deleted_count,
            "filters": {
                "delete_all": delete_all,
                "before_days": before_days,
                "before_date": before_date.isoformat() if before_days else None,
                "metric_name": metric_name
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete metrics: {str(e)}")


@router.get("/observability/stats")
async def get_observability_stats():
    """Get observability statistics"""
    try:
        log_count = await observability_db.get_log_count()
        trace_count = await observability_db.get_trace_count()
        metric_count = await observability_db.get_metric_count()
        
        return {
            "log_count": log_count,
            "trace_count": trace_count,
            "metric_count": metric_count,
            "total": log_count + trace_count + metric_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")


@router.get("/observability/database")
async def get_database_stats():
    """Get database statistics and recent data"""
    try:
        async with async_engine.begin() as conn:
            # Get table row counts
            tables = ["chats", "messages", "users", "memories", "agent_executions"]
            table_stats = {}
            
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                table_stats[table] = count
            
            # Get recent chats
            chats_result = await conn.execute(
                select(Chat).order_by(Chat.created_at.desc()).limit(5)
            )
            recent_chats = []
            for chat in chats_result:
                recent_chats.append({
                    "id": chat.id,
                    "title": chat.title,
                    "status": chat.status.value,
                    "created_at": chat.created_at.isoformat()
                })
            
            # Get recent messages
            messages_result = await conn.execute(
                select(Message).order_by(Message.created_at.desc()).limit(5)
            )
            recent_messages = []
            for msg in messages_result:
                recent_messages.append({
                    "id": msg.id,
                    "chat_id": msg.chat_id,
                    "role": msg.role.value,
                    "content": msg.content[:100] + "..." if len(msg.content) > 100 else msg.content,
                    "created_at": msg.created_at.isoformat()
                })
            
            # Get recent agent executions
            executions_result = await conn.execute(
                select(AgentExecution).order_by(AgentExecution.created_at.desc()).limit(5)
            )
            recent_executions = []
            for exec in executions_result:
                recent_executions.append({
                    "id": exec.id,
                    "chat_id": exec.chat_id,
                    "agent_name": exec.agent_name,
                    "status": exec.status,
                    "execution_time": exec.execution_time,
                    "created_at": exec.created_at.isoformat()
                })
        
        return {
            "table_stats": table_stats,
            "recent_chats": recent_chats,
            "recent_messages": recent_messages,
            "recent_executions": recent_executions,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get database stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve database stats")


@router.get("/observability/redis")
async def get_redis_stats():
    """Get Redis cache statistics and data"""
    try:
        # Get Redis info
        info = await redis_manager.redis.info()
        
        # Get all keys
        all_keys = await redis_manager.redis.keys("*")
        
        # Categorize keys
        key_categories = {
            "metric": [],
            "timing": [],
            "gauge": [],
            "error": [],
            "chat": [],
            "other": []
        }
        
        for key in all_keys:
            if key.startswith("metric:"):
                key_categories["metric"].append(key)
            elif key.startswith("timing:"):
                key_categories["timing"].append(key)
            elif key.startswith("gauge:"):
                key_categories["gauge"].append(key)
            elif key.startswith("error:"):
                key_categories["error"].append(key)
            elif key.startswith("chat:"):
                key_categories["chat"].append(key)
            else:
                key_categories["other"].append(key)
        
        # Get sample data from each category
        sample_data = {}
        for category, keys in key_categories.items():
            if keys:
                sample_key = keys[0]
                sample_value = await redis_manager.get(sample_key)
                sample_data[category] = {
                    "key": sample_key,
                    "value": sample_value,
                    "total_keys": len(keys)
                }
        
        return {
            "redis_info": {
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_keys": info.get("db0", {}).get("keys"),
                "uptime_in_seconds": info.get("uptime_in_seconds")
            },
            "key_categories": {k: len(v) for k, v in key_categories.items()},
            "sample_data": sample_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get Redis stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Redis stats")
