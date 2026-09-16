import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.redis import redis_manager


class RuntimeState:
    """Redis-based runtime state management (working memory)"""
    
    def __init__(self):
        self.logger = logging.getLogger("runtime_state")
        
        # TTL configurations (as specified)
        self.CONVERSATION_TTL = 86400  # 24 hours
        self.AGENT_STATE_TTL = 14400  # 4 hours
        self.TOOL_CACHE_TTL_MIN = 300  # 5 minutes
        self.TOOL_CACHE_TTL_MAX = 900  # 15 minutes
        self.RESPONSE_CACHE_TTL = 3600  # 1 hour
        self.WORKFLOW_TTL = 14400  # 4 hours
        self.SCREENSHOT_CACHE_TTL = 86400  # 24 hours
    
    async def store_conversation_context(
        self,
        chat_id: int,
        context: Dict[str, Any]
    ):
        """Store conversation context in Redis"""
        key = f"conversation:{chat_id}"
        await redis_manager.set(key, context, self.CONVERSATION_TTL)
        self.logger.debug(f"Conversation context stored for chat {chat_id}")
    
    async def get_conversation_context(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve conversation context from Redis"""
        key = f"conversation:{chat_id}"
        return await redis_manager.get(key)
    
    async def add_message_to_conversation(
        self,
        chat_id: int,
        message: Dict[str, Any]
    ):
        """Add a message to the conversation buffer"""
        key = f"conversation:{chat_id}:messages"
        
        # Get existing messages
        messages = await redis_manager.get(key) or []
        
        # Add new message
        messages.append(message)
        
        # Keep only last 50 messages
        if len(messages) > 50:
            messages = messages[-50:]
        
        await redis_manager.set(key, messages, self.CONVERSATION_TTL)
        self.logger.debug(f"Message added to conversation buffer for chat {chat_id}")
    
    async def get_conversation_messages(self, chat_id: int) -> List[Dict[str, Any]]:
        """Get conversation message buffer"""
        key = f"conversation:{chat_id}:messages"
        return await redis_manager.get(key) or []
    
    async def store_agent_state(
        self,
        agent_name: str,
        state: Dict[str, Any]
    ):
        """Store agent state in Redis"""
        key = f"agent_state:{agent_name}"
        await redis_manager.set(key, state, self.AGENT_STATE_TTL)
        self.logger.debug(f"Agent state stored for {agent_name}")
    
    async def get_agent_state(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent state from Redis"""
        key = f"agent_state:{agent_name}"
        return await redis_manager.get(key)
    
    async def update_agent_progress(
        self,
        agent_name: str,
        progress: Dict[str, Any]
    ):
        """Update agent progress in state"""
        key = f"agent_state:{agent_name}"
        current_state = await redis_manager.get(key) or {}
        current_state.update(progress)
        await redis_manager.set(key, current_state, self.AGENT_STATE_TTL)
        self.logger.debug(f"Agent progress updated for {agent_name}")
    
    async def cache_response(
        self,
        cache_key: str,
        response: Any,
        ttl: Optional[int] = None
    ):
        """Cache LLM response in Redis"""
        ttl = ttl or self.RESPONSE_CACHE_TTL
        await redis_manager.set(f"response:{cache_key}", response, ttl)
        self.logger.debug(f"Response cached with key: {cache_key}")
    
    async def get_cached_response(self, cache_key: str) -> Optional[Any]:
        """Get cached response from Redis"""
        return await redis_manager.get(f"response:{cache_key}")
    
    async def cache_tool_result(
        self,
        tool_name: str,
        tool_params: Dict[str, Any],
        result: Any,
        ttl: Optional[int] = None
    ):
        """Cache tool execution result"""
        ttl = ttl or self.TOOL_CACHE_TTL_MIN  # Default to 5 minutes
        # Create cache key from tool name and params
        cache_key = f"tool:{tool_name}:{hash(json.dumps(tool_params, sort_keys=True))}"
        await redis_manager.set(cache_key, result, ttl)
        self.logger.debug(f"Tool result cached for {tool_name} with TTL {ttl}s")
    
    async def get_cached_tool_result(
        self,
        tool_name: str,
        tool_params: Dict[str, Any]
    ) -> Optional[Any]:
        """Get cached tool result"""
        cache_key = f"tool:{tool_name}:{hash(json.dumps(tool_params, sort_keys=True))}"
        return await redis_manager.get(cache_key)
    
    async def cache_screenshot(
        self,
        screenshot_id: str,
        screenshot_data: Any,
        ttl: Optional[int] = None
    ):
        """Cache screenshot data"""
        ttl = ttl or self.SCREENSHOT_CACHE_TTL
        await redis_manager.set(f"screenshot:{screenshot_id}", screenshot_data, ttl)
        self.logger.debug(f"Screenshot cached with ID {screenshot_id}")
    
    async def get_cached_screenshot(self, screenshot_id: str) -> Optional[Any]:
        """Get cached screenshot"""
        return await redis_manager.get(f"screenshot:{screenshot_id}")
    
    async def store_workflow_state(
        self,
        workflow_id: str,
        state: Dict[str, Any]
    ):
        """Store workflow state in Redis"""
        key = f"workflow:{workflow_id}"
        await redis_manager.set(key, state, self.WORKFLOW_TTL)
        self.logger.debug(f"Workflow state stored for {workflow_id}")
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow state from Redis"""
        key = f"workflow:{workflow_id}"
        return await redis_manager.get(key)
    
    async def update_workflow_progress(
        self,
        workflow_id: str,
        step: str,
        percent_complete: float,
        status: str = "running"
    ):
        """Update workflow progress"""
        key = f"workflow:{workflow_id}"
        current_state = await redis_manager.get(key) or {}
        current_state.update({
            "current_step": step,
            "percent_complete": percent_complete,
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        })
        await redis_manager.set(key, current_state, self.WORKFLOW_TTL)
        self.logger.debug(f"Workflow progress updated for {workflow_id}: {step} ({percent_complete}%)")
    
    async def queue_memory_extraction(
        self,
        user_id: int,
        content: str,
        context: Dict[str, Any]
    ):
        """Queue memory extraction for background processing"""
        key = f"memory_queue:{user_id}"
        
        # Get existing queue
        queue = await redis_manager.get(key) or []
        
        # Add new memory extraction task
        queue.append({
            "content": content,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await redis_manager.set(key, queue, self.CONVERSATION_TTL)
        self.logger.debug(f"Memory extraction queued for user {user_id}")
    
    async def get_memory_queue(self, user_id: int) -> List[Dict[str, Any]]:
        """Get memory extraction queue"""
        key = f"memory_queue:{user_id}"
        return await redis_manager.get(key) or []
    
    async def clear_conversation(self, chat_id: int):
        """Clear conversation data from Redis"""
        await redis_manager.delete(f"conversation:{chat_id}")
        await redis_manager.delete(f"conversation:{chat_id}:messages")
        self.logger.debug(f"Conversation data cleared for chat {chat_id}")
    
    async def clear_agent_state(self, agent_name: str):
        """Clear agent state from Redis"""
        await redis_manager.delete(f"agent_state:{agent_name}")
        self.logger.debug(f"Agent state cleared for {agent_name}")
    
    async def clear_workflow(self, workflow_id: str):
        """Clear workflow state from Redis"""
        await redis_manager.delete(f"workflow:{workflow_id}")
        self.logger.debug(f"Workflow state cleared for {workflow_id}")


# Global instance
runtime_state = RuntimeState()