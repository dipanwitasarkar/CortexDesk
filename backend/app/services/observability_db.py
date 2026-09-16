import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from app.core.database import get_async_db
from app.models.memory import ObservabilityMetric, ObservabilityTrace, ObservabilityLog
from sqlalchemy import select, and_, func


class ObservabilityDB:
    """PostgreSQL-based observability storage for metrics, traces, and logs"""
    
    def __init__(self):
        self.logger = logging.getLogger("observability_db")
    
    async def record_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_type: str = "gauge",
        tags: Optional[Dict[str, Any]] = None
    ):
        """Record a metric in PostgreSQL"""
        async for db in get_async_db():
            metric = ObservabilityMetric(
                metric_name=metric_name,
                metric_value=metric_value,
                metric_type=metric_type,
                tags=tags or {}
            )
            db.add(metric)
            await db.commit()
            
            self.logger.debug(f"Metric recorded: {metric_name}", value=metric_value, type=metric_type)
    
    async def record_trace(
        self,
        trace_id: str,
        span_id: str,
        operation_name: str,
        service_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        parent_span_id: Optional[str] = None,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a trace span in PostgreSQL"""
        async for db in get_async_db():
            duration_ms = None
            if end_time:
                duration_ms = (end_time - start_time).total_seconds() * 1000
            
            trace = ObservabilityTrace(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                operation_name=operation_name,
                service_name=service_name,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                status=status,
                meta_data=metadata or {}
            )
            db.add(trace)
            await db.commit()
            
            self.logger.debug(f"Trace recorded: {operation_name}", trace_id=trace_id, duration_ms=duration_ms)
    
    async def record_log(
        self,
        level: str,
        logger_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Record a log entry in PostgreSQL"""
        async for db in get_async_db():
            log = ObservabilityLog(
                level=level,
                logger_name=logger_name,
                message=message,
                context=context or {}
            )
            db.add(log)
            await db.commit()
            
            self.logger.debug(f"Log recorded: {level} - {message}")
    
    async def get_metrics(
        self,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve metrics from PostgreSQL"""
        async for db in get_async_db():
            query = select(ObservabilityMetric)
            
            conditions = []
            if metric_name:
                conditions.append(ObservabilityMetric.metric_name == metric_name)
            if start_time:
                conditions.append(ObservabilityMetric.timestamp >= start_time)
            if end_time:
                conditions.append(ObservabilityMetric.timestamp <= end_time)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(ObservabilityMetric.timestamp.desc()).limit(limit)
            result = await db.execute(query)
            metrics = result.scalars().all()
            
            return [
                {
                    "id": m.id,
                    "metric_name": m.metric_name,
                    "metric_value": m.metric_value,
                    "metric_type": m.metric_type,
                    "tags": m.tags,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in metrics
            ]
    
    async def get_traces(
        self,
        trace_id: Optional[str] = None,
        service_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve traces from PostgreSQL"""
        async for db in get_async_db():
            query = select(ObservabilityTrace)
            
            conditions = []
            if trace_id:
                conditions.append(ObservabilityTrace.trace_id == trace_id)
            if service_name:
                conditions.append(ObservabilityTrace.service_name == service_name)
            if start_time:
                conditions.append(ObservabilityTrace.start_time >= start_time)
            if end_time:
                conditions.append(ObservabilityTrace.start_time <= end_time)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(ObservabilityTrace.start_time.desc()).limit(limit)
            result = await db.execute(query)
            traces = result.scalars().all()
            
            return [
                {
                    "id": t.id,
                    "trace_id": t.trace_id,
                    "span_id": t.span_id,
                    "parent_span_id": t.parent_span_id,
                    "operation_name": t.operation_name,
                    "service_name": t.service_name,
                    "start_time": t.start_time.isoformat(),
                    "end_time": t.end_time.isoformat() if t.end_time else None,
                    "duration_ms": t.duration_ms,
                    "status": t.status,
                    "metadata": t.meta_data
                }
                for t in traces
            ]
    
    async def get_logs(
        self,
        level: Optional[str] = None,
        logger_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve logs from PostgreSQL"""
        async for db in get_async_db():
            query = select(ObservabilityLog)
            
            conditions = []
            if level:
                conditions.append(ObservabilityLog.level == level)
            if logger_name:
                conditions.append(ObservabilityLog.logger_name == logger_name)
            if start_time:
                conditions.append(ObservabilityLog.timestamp >= start_time)
            if end_time:
                conditions.append(ObservabilityLog.timestamp <= end_time)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            query = query.order_by(ObservabilityLog.timestamp.desc()).limit(limit)
            result = await db.execute(query)
            logs = result.scalars().all()
            
            return [
                {
                    "id": l.id,
                    "level": l.level,
                    "logger_name": l.logger_name,
                    "message": l.message,
                    "context": l.context,
                    "timestamp": l.timestamp.isoformat()
                }
                for l in logs
            ]
    
    async def delete_logs(
        self,
        before_date: Optional[datetime] = None,
        level: Optional[str] = None,
        logger_name: Optional[str] = None
    ) -> int:
        """Delete logs from PostgreSQL with optional filters"""
        async for db in get_async_db():
            from sqlalchemy import delete
            
            conditions = []
            if before_date:
                conditions.append(ObservabilityLog.timestamp < before_date)
            if level:
                conditions.append(ObservabilityLog.level == level)
            if logger_name:
                conditions.append(ObservabilityLog.logger_name == logger_name)
            
            delete_query = delete(ObservabilityLog)
            if conditions:
                delete_query = delete_query.where(and_(*conditions))
            
            result = await db.execute(delete_query)
            await db.commit()
            
            return result.rowcount
    
    async def delete_traces(
        self,
        before_date: Optional[datetime] = None,
        service_name: Optional[str] = None
    ) -> int:
        """Delete traces from PostgreSQL with optional filters"""
        async for db in get_async_db():
            from sqlalchemy import delete
            
            conditions = []
            if before_date:
                conditions.append(ObservabilityTrace.timestamp < before_date)
            if service_name:
                conditions.append(ObservabilityTrace.service_name == service_name)
            
            delete_query = delete(ObservabilityTrace)
            if conditions:
                delete_query = delete_query.where(and_(*conditions))
            
            result = await db.execute(delete_query)
            await db.commit()
            
            return result.rowcount
    
    async def delete_metrics(
        self,
        before_date: Optional[datetime] = None,
        metric_name: Optional[str] = None
    ) -> int:
        """Delete metrics from PostgreSQL with optional filters"""
        async for db in get_async_db():
            from sqlalchemy import delete
            
            conditions = []
            if before_date:
                conditions.append(ObservabilityMetric.timestamp < before_date)
            if metric_name:
                conditions.append(ObservabilityMetric.metric_name == metric_name)
            
            delete_query = delete(ObservabilityMetric)
            if conditions:
                delete_query = delete_query.where(and_(*conditions))
            
            result = await db.execute(delete_query)
            await db.commit()
            
            return result.rowcount
    
    async def get_log_count(self) -> int:
        """Get total count of logs"""
        async for db in get_async_db():
            result = await db.execute(select(func.count()).select_from(ObservabilityLog))
            return result.scalar()
    
    async def get_trace_count(self) -> int:
        """Get total count of traces"""
        async for db in get_async_db():
            result = await db.execute(select(func.count()).select_from(ObservabilityTrace))
            return result.scalar()
    
    async def get_metric_count(self) -> int:
        """Get total count of metrics"""
        async for db in get_async_db():
            result = await db.execute(select(func.count()).select_from(ObservabilityMetric))
            return result.scalar()


# Global instance
observability_db = ObservabilityDB()