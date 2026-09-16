from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service
from app.services.observability import logger, performance_monitor, error_tracker, tracer
from app.core.config import settings
import time


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
        request_id = tracer.generate_request_id()
        start_time = time.time()
        
        logger.info(f"Agent execution started: {self.name}", 
                   agent=self.name, request_id=request_id, chat_id=chat_id)
        
        try:
            # Execute the agent
            result = await self.process(input_data)
            execution_time = time.time() - start_time
            
            # Track performance
            await performance_monitor.track_agent_performance(
                agent_name=self.name,
                operation="execute",
                duration=execution_time,
                success=True,
                chat_id=chat_id,
                request_id=request_id
            )
            
            # Log successful execution
            await memory_service.log_agent_execution(
                chat_id=chat_id,
                agent_name=self.name,
                input_prompt=str(input_data),
                output_response=str(result),
                execution_time=execution_time,
                status="completed"
            )
            
            logger.info(f"Agent execution completed: {self.name}", 
                       agent=self.name, request_id=request_id, 
                       execution_time=execution_time, success=True)
            
            return {
                "success": True,
                "agent": self.name,
                "result": result,
                "execution_time": execution_time,
                "request_id": request_id
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Track performance
            await performance_monitor.track_agent_performance(
                agent_name=self.name,
                operation="execute",
                duration=execution_time,
                success=False,
                chat_id=chat_id,
                request_id=request_id
            )
            
            # Track error
            await error_tracker.track_error(
                e,
                context={
                    "agent": self.name,
                    "chat_id": chat_id,
                    "request_id": request_id,
                    "input_data": str(input_data)
                }
            )
            
            # Log failed execution
            await memory_service.log_agent_execution(
                chat_id=chat_id,
                agent_name=self.name,
                input_prompt=str(input_data),
                error_message=str(e),
                execution_time=execution_time,
                status="failed"
            )
            
            logger.error(f"Agent execution failed: {self.name}", 
                        agent=self.name, request_id=request_id, 
                        execution_time=execution_time, error=str(e))
            
            return {
                "success": False,
                "agent": self.name,
                "error": str(e),
                "execution_time": execution_time,
                "request_id": request_id
            }

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
