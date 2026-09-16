import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps
from contextlib import contextmanager
from app.core.config import settings
from app.core.redis import redis_manager


class StructuredLogger:
    """Structured logging with JSON format and context tracking"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.log_level))
        
        # Console handler with JSON formatting
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)
        
        # File handler if configured
        if settings.log_file:
            file_handler = logging.FileHandler(settings.log_file)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def log(self, level: str, message: str, **kwargs):
        """Log a message with structured context"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            **kwargs
        }
        
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(json.dumps(log_data))
    
    def info(self, message: str, **kwargs):
        self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self.log("DEBUG", message, **kwargs)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class MetricsCollector:
    """Collect and track system metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.logger = StructuredLogger("metrics")
    
    async def increment(self, metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = f"metric:{metric_name}"
        if tags:
            key += f":{json.dumps(tags, sort_keys=True)}"
        
        current = await redis_manager.get(key) or 0
        await redis_manager.set(key, int(current) + value, ttl=86400)
        
        self.logger.debug(f"Metric incremented: {metric_name}", value=value, tags=tags)
    
    async def timing(self, metric_name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """Record a timing metric"""
        key = f"timing:{metric_name}"
        if tags:
            key += f":{json.dumps(tags, sort_keys=True)}"
        
        # Store recent timings
        timings = await redis_manager.get(key) or []
        timings.append(duration)
        if len(timings) > 100:  # Keep last 100
            timings = timings[-100:]
        
        await redis_manager.set(key, timings, ttl=86400)
        
        self.logger.debug(f"Timing recorded: {metric_name}", duration=duration, tags=tags)
    
    async def gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a gauge metric"""
        key = f"gauge:{metric_name}"
        if tags:
            key += f":{json.dumps(tags, sort_keys=True)}"
        
        await redis_manager.set(key, value, ttl=3600)
        
        self.logger.debug(f"Gauge recorded: {metric_name}", value=value, tags=tags)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        # This would typically query Redis for all metrics
        return {
            "status": "metrics_available",
            "timestamp": datetime.utcnow().isoformat()
        }


class RequestTracer:
    """Trace requests across the system for debugging"""
    
    def __init__(self):
        self.logger = StructuredLogger("tracer")
    
    def generate_request_id(self) -> str:
        """Generate a unique request ID"""
        return str(uuid.uuid4())
    
    @contextmanager
    def trace_request(self, request_id: str, operation: str, **context):
        """Context manager for tracing a request"""
        start_time = time.time()
        
        self.logger.info(
            f"Request started: {operation}",
            request_id=request_id,
            operation=operation,
            context=context
        )
        
        try:
            yield request_id
            
            duration = time.time() - start_time
            self.logger.info(
                f"Request completed: {operation}",
                request_id=request_id,
                operation=operation,
                duration=duration,
                status="success"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Request failed: {operation}",
                request_id=request_id,
                operation=operation,
                duration=duration,
                status="error",
                error=str(e),
                error_type=type(e).__name__
            )
            raise


class PerformanceMonitor:
    """Monitor system performance and resource usage"""
    
    def __init__(self):
        self.logger = StructuredLogger("performance")
        self.metrics = MetricsCollector()
    
    async def track_agent_performance(
        self,
        agent_name: str,
        operation: str,
        duration: float,
        success: bool,
        **metadata
    ):
        """Track agent execution performance"""
        await self.metrics.timing(
            f"agent.{agent_name}.{operation}",
            duration,
            tags={"success": str(success)}
        )
        
        if success:
            await self.metrics.increment(
                f"agent.{agent_name}.success",
                tags={"operation": operation}
            )
        else:
            await self.metrics.increment(
                f"agent.{agent_name}.error",
                tags={"operation": operation}
            )
        
        self.logger.info(
            f"Agent performance: {agent_name}",
            agent=agent_name,
            operation=operation,
            duration=duration,
            success=success,
            **metadata
        )
    
    async def track_llm_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        duration: float
    ):
        """Track LLM API usage"""
        await self.metrics.increment(
            "llm.tokens.total",
            value=total_tokens,
            tags={"model": model}
        )
        
        await self.metrics.timing(
            "llm.request.duration",
            duration,
            tags={"model": model}
        )
        
        self.logger.info(
            "LLM usage tracked",
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            duration=duration
        )
    
    async def track_memory_usage(self):
        """Track system memory usage"""
        import psutil
        
        memory = psutil.virtual_memory()
        await self.metrics.gauge(
            "system.memory.percent",
            memory.percent,
            tags={"type": "usage"}
        )
        
        await self.metrics.gauge(
            "system.memory.available",
            memory.available,
            tags={"type": "available"}
        )
        
        self.logger.debug(
            "Memory usage tracked",
            percent=memory.percent,
            available=memory.available
        )
    
    async def track_cpu_usage(self):
        """Track CPU usage"""
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        await self.metrics.gauge(
            "system.cpu.percent",
            cpu_percent,
            tags={"type": "usage"}
        )
        
        self.logger.debug("CPU usage tracked", percent=cpu_percent)


class ErrorTracker:
    """Track and analyze errors"""
    
    def __init__(self):
        self.logger = StructuredLogger("errors")
        self.metrics = MetricsCollector()
    
    async def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error"
    ):
        """Track an error with context"""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {}
        }
        
        # Increment error counter
        await self.metrics.increment(
            "errors.total",
            tags={
                "type": type(error).__name__,
                "severity": severity
            }
        )
        
        # Store error details
        error_key = f"error:{type(error).__name__}:{int(time.time())}"
        await redis_manager.set(error_key, error_data, ttl=604800)  # 7 days
        
        self.logger.error(
            f"Error tracked: {type(error).__name__}",
            **error_data
        )
    
    async def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent errors"""
        # This would query Redis for recent errors
        return []


def track_performance(operation: str):
    """Decorator to track function performance"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                await monitor.track_agent_performance(
                    agent_name=func.__module__.split('.')[-1],
                    operation=operation,
                    duration=duration,
                    success=True
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                await monitor.track_agent_performance(
                    agent_name=func.__module__.split('.')[-1],
                    operation=operation,
                    duration=duration,
                    success=False
                )
                
                error_tracker = ErrorTracker()
                await error_tracker.track_error(e, {"operation": operation})
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = PerformanceMonitor()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # For sync functions, we'd need to run this in an async context
                # For now, just log it
                monitor.logger.info(
                    f"Sync function performance: {operation}",
                    duration=duration,
                    function=func.__name__
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                monitor.logger.error(
                    f"Sync function error: {operation}",
                    duration=duration,
                    function=func.__name__,
                    error=str(e)
                )
                
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global instances
logger = StructuredLogger("app")
metrics = MetricsCollector()
tracer = RequestTracer()
performance_monitor = PerformanceMonitor()
error_tracker = ErrorTracker()

# Import asyncio at the end to avoid circular imports
import asyncio
