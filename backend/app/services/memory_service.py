from app.core.database import get_async_db
from app.core.redis import redis_manager
from app.core.qdrant import qdrant_manager
from app.services.llm_service import llm_service
from app.models.memory import Memory, MemoryType, AgentExecution
from app.models.chat import Chat, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class MemoryService:
    def __init__(self):
        self.session_memory_ttl = 3600  # 1 hour
        self.context_memory_ttl = 86400  # 24 hours

    async def store_conversation_context(
        self,
        chat_id: int,
        context: Dict[str, Any]
    ):
        """Store conversation context in Redis"""
        key = f"chat_context:{chat_id}"
        await redis_manager.set(key, context, self.context_memory_ttl)

    async def get_conversation_context(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve conversation context from Redis"""
        key = f"chat_context:{chat_id}"
        return await redis_manager.get(key)

    async def store_agent_state(
        self,
        agent_name: str,
        state: Dict[str, Any]
    ):
        """Store agent state in Redis"""
        key = f"agent_state:{agent_name}"
        await redis_manager.set(key, state, self.session_memory_ttl)

    async def get_agent_state(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent state from Redis"""
        key = f"agent_state:{agent_name}"
        return await redis_manager.get(key)

    async def store_long_term_memory(
        self,
        user_id: int,
        memory_type: MemoryType,
        content: str,
        importance: float = 0.5,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Store long-term memory in PostgreSQL and Qdrant"""
        async for db in get_async_db():
            # Generate embedding
            embedding = await llm_service.generate_embedding(content)
            
            # Store in PostgreSQL
            memory = Memory(
                user_id=user_id,
                memory_type=memory_type,
                content=content,
                importance=importance,
                source=source,
                metadata=json.dumps(metadata) if metadata else None
            )
            db.add(memory)
            await db.commit()
            await db.refresh(memory)
            
            # Store in Qdrant
            await qdrant_manager.create_collection("ai_assistant_memory", vector_size=384)
            await qdrant_manager.insert_points(
                "ai_assistant_memory",
                [{
                    "id": str(memory.id),
                    "vector": embedding,
                    "payload": {
                        "user_id": user_id,
                        "memory_type": memory_type.value,
                        "content": content,
                        "importance": importance,
                        "source": source,
                        "created_at": memory.created_at.isoformat()
                    }
                }]
            )
            
            # Update embedding_id in PostgreSQL
            memory.embedding_id = str(memory.id)
            await db.commit()
            
            return memory.id

    async def retrieve_memories(
        self,
        user_id: int,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories using semantic search"""
        # Generate query embedding
        query_embedding = await llm_service.generate_embedding(query)
        
        # Build filter
        filter_dict = {"user_id": user_id}
        if memory_type:
            filter_dict["memory_type"] = memory_type.value
        
        # Search Qdrant
        results = await qdrant_manager.search(
            "ai_assistant_memory",
            query_embedding,
            limit=limit,
            filter_dict=filter_dict
        )
        
        return results

    async def log_agent_execution(
        self,
        chat_id: int,
        agent_name: str,
        input_prompt: str,
        output_response: Optional[str] = None,
        execution_time: Optional[float] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        error_message: Optional[str] = None,
        status: str = "completed"
    ) -> int:
        """Log agent execution for observability"""
        async for db in get_async_db():
            execution = AgentExecution(
                chat_id=chat_id,
                agent_name=agent_name,
                input_prompt=input_prompt,
                output_response=output_response,
                execution_time=execution_time,
                tool_calls=json.dumps(tool_calls) if tool_calls else None,
                error_message=error_message,
                status=status
            )
            db.add(execution)
            await db.commit()
            await db.refresh(execution)
            
            return execution.id

    async def get_chat_history(
        self,
        chat_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve chat history from PostgreSQL"""
        async for db in get_async_db():
            result = await db.execute(
                select(Message)
                .where(Message.chat_id == chat_id)
                .order_by(Message.created_at)
                .limit(limit)
            )
            messages = result.scalars().all()
            
            return [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "agent_used": msg.agent_used,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]

    async def cache_response(
        self,
        cache_key: str,
        response: Any,
        ttl: Optional[int] = None
    ):
        """Cache response in Redis"""
        await redis_manager.set(cache_key, response, ttl)

    async def get_cached_response(self, cache_key: str) -> Optional[Any]:
        """Get cached response from Redis"""
        return await redis_manager.get(cache_key)


memory_service = MemoryService()
