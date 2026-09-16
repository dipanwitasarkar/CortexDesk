from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service
from app.services.observability_db import observability_db
from app.core.config import settings
import time
import uuid
from datetime import datetime


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.timeout = settings.agent_timeout

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return response"""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass

    async def execute_with_logging(
        self,
        chat_id: int,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agent with logging and error handling"""
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        # Log agent start
        await observability_db.record_log(
            level="INFO",
            logger_name=self.name,
            message=f"{self.name} agent started execution",
            context={"request_id": request_id, "chat_id": chat_id, "input": str(input_data)[:100]}
        )
        
        # Record trace start
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        await observability_db.record_trace(
            trace_id=trace_id,
            span_id=span_id,
            operation_name=f"{self.name}.execute",
            service_name=self.name,
            start_time=start_time,
            status="running"
        )
        
        try:
            # Execute the agent
            result = await self.process(input_data)
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Record trace completion
            await observability_db.record_trace(
                trace_id=trace_id,
                span_id=span_id,
                operation_name=f"{self.name}.execute",
                service_name=self.name,
                start_time=start_time,
                end_time=end_time,
                status="success",
                metadata={"execution_time": execution_time, "result_keys": list(result.keys())}
            )
            
            # Log successful execution
            await observability_db.record_log(
                level="INFO",
                logger_name=self.name,
                message=f"{self.name} agent completed successfully",
                context={"request_id": request_id, "chat_id": chat_id, "execution_time": execution_time}
            )
            
            # Record success metric
            await observability_db.record_metric(
                metric_name=f"agent.{self.name}.success",
                metric_value=1,
                metric_type="counter",
                tags={"operation": "execute"}
            )
            
            # Log to memory service
            await memory_service.log_agent_execution(
                chat_id=chat_id,
                agent_name=self.name,
                input_prompt=str(input_data),
                output_response=str(result),
                execution_time=execution_time,
                status="completed"
            )
            
            return {
                "success": True,
                "agent": self.name,
                "result": result,
                "execution_time": execution_time,
                "request_id": request_id
            }
            
        except Exception as e:
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            # Record trace failure
            await observability_db.record_trace(
                trace_id=trace_id,
                span_id=span_id,
                operation_name=f"{self.name}.execute",
                service_name=self.name,
                start_time=start_time,
                end_time=end_time,
                status="error",
                metadata={"error": str(e), "execution_time": execution_time}
            )
            
            # Log agent error
            await observability_db.record_log(
                level="ERROR",
                logger_name=self.name,
                message=f"{self.name} agent failed: {str(e)}",
                context={"request_id": request_id, "chat_id": chat_id, "error": str(e)}
            )
            
            # Record error metric
            await observability_db.record_metric(
                metric_name=f"agent.{self.name}.error",
                metric_value=1,
                metric_type="counter",
                tags={"operation": "execute", "error_type": type(e).__name__}
            )
            
            # Log to memory service
            await memory_service.log_agent_execution(
                chat_id=chat_id,
                agent_name=self.name,
                input_prompt=str(input_data),
                error_message=str(e),
                execution_time=execution_time,
                status="failed"
            )
            
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "execution_time": execution_time,
                "request_id": request_id
            }

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with logging (called by supervisor)"""
        chat_id = input_data.get("chat_id")
        return await self.execute_with_logging(chat_id, input_data)

    async def call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None
    ) -> str:
        """Call LLM with system prompt"""
        system_message = {"role": "system", "content": self.get_system_prompt()}
        all_messages = [system_message] + messages
        
        return await llm_service.generate_response(all_messages, temperature)

    async def get_relevant_context(
        self,
        user_id: int,
        query: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant context from memory"""
        memories = await memory_service.retrieve_memories(
            user_id=user_id,
            query=query,
            limit=limit
        )
        return memories
