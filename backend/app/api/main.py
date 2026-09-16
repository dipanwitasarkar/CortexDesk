from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.core.database import get_async_db
from app.api.schemas import (
    ChatCreate, ChatResponse, ChatWithMessages,
    MessageCreate, MessageResponse,
    AssistantRequest, AssistantResponse
)
from app.models.chat import Chat, Message, ChatStatus, MessageRole
from app.models.user import User
from app.models.memory import AgentExecution
from app.services.runtime_state import runtime_state
from app.services.llm_service import llm_service
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.code_agent import CodeAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.windows_agent import WindowsAgent
from app.agents.system_agent import SystemAgent
from app.agents.productivity_agent import ProductivityAgent
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize agents
def get_supervisor_agent():
    """Initialize and return the supervisor agent with all sub-agents"""
    agents = [
        CodeAgent(),
        KnowledgeAgent(),
        WindowsAgent(),
        SystemAgent(),
        ProductivityAgent()
    ]
    return SupervisorAgent(agents)


@router.post("/chats", response_model=ChatResponse)
async def create_chat(
    chat: ChatCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new chat session"""
    # Verify user exists, create if not
    result = await db.execute(select(User).where(User.id == chat.user_id))
    user = result.scalar_one_or_none()
    if not user:
        # Auto-create user for demo purposes
        user = User(
            id=chat.user_id,
            username=f"user_{chat.user_id}",
            email=f"user_{chat.user_id}@example.com",
            hashed_password="demo",  # Not used in this demo
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Create chat with placeholder title
    db_chat = Chat(
        user_id=chat.user_id,
        title="New conversation",
        context=json.dumps(chat.context) if chat.context else None,
        meta_data=json.dumps(chat.meta_data) if chat.meta_data else None
    )
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    
    return db_chat


@router.get("/chats/{chat_id}", response_model=ChatWithMessages)
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a chat with its messages"""
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Get messages
    messages_result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at)
    )
    messages = messages_result.scalars().all()
    
    return ChatWithMessages(
        **chat.__dict__,
        messages=[MessageResponse.model_validate(msg) for msg in messages]
    )


@router.get("/chats", response_model=List[ChatResponse])
async def list_chats(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_db)
):
    """List all chats for a user"""
    result = await db.execute(
        select(Chat)
        .where(Chat.user_id == user_id)
        .where(Chat.status == ChatStatus.ACTIVE)
        .order_by(Chat.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    chats = result.scalars().all()
    return chats


@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a chat and all its messages"""
    # Get the chat
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Delete all agent executions for this chat (foreign key dependency)
    await db.execute(
        delete(AgentExecution).where(AgentExecution.chat_id == chat_id)
    )
    
    # Delete all messages in the chat
    await db.execute(
        delete(Message).where(Message.chat_id == chat_id)
    )
    
    # Delete the chat
    await db.execute(delete(Chat).where(Chat.id == chat_id))
    
    await db.commit()
    
    # Clear Redis runtime state for this chat
    await runtime_state.clear_conversation(chat_id)
    
    return {"message": "Chat deleted successfully"}


@router.post("/chats/{chat_id}/messages", response_model=MessageResponse)
async def create_message(
    chat_id: int,
    message: MessageCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Add a message to a chat"""
    # Verify chat exists
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Create message
    db_message = Message(
        chat_id=chat_id,
        role=MessageRole(message.role),
        content=message.content,
        agent_used=message.agent_used,
        tool_calls=json.dumps(message.tool_calls) if message.tool_calls else None,
        meta_data=json.dumps(message.meta_data) if message.meta_data else None
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    
    # Update chat timestamp
    chat.updated_at = chat.updated_at  # This will trigger the onupdate
    await db.commit()
    
    return db_message


@router.post("/assistant", response_model=AssistantResponse)
async def assistant(
    request: AssistantRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Process a user message through the assistant"""
    
    # Get or create chat
    if request.chat_id:
        result = await db.execute(select(Chat).where(Chat.id == request.chat_id))
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
    else:
        # Create new chat with first message as title
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        chat = Chat(
            user_id=request.user_id,
            title=title
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
    
    # Update chat title if it's still "New conversation" and this is the first message
    if chat.title == "New conversation":
        # Check if this is the first message
        message_count_result = await db.execute(
            select(func.count()).select_from(Message).where(Message.chat_id == chat.id)
        )
        message_count = message_count_result.scalar()
        
        if message_count == 0:  # This is the first message
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            chat.title = title
            await db.commit()
    
    # Store user message
    user_message = Message(
        chat_id=chat.id,
        role=MessageRole.USER,
        content=request.message
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    # Store in Redis runtime state (conversation buffer)
    await runtime_state.add_message_to_conversation(
        chat_id=chat.id,
        message={
            "id": user_message.id,
            "role": "user",
            "content": request.message,
            "timestamp": user_message.created_at.isoformat()
        }
    )
    
    # Get chat context
    context = {}
    if chat.context:
        try:
            context = json.loads(chat.context)
        except json.JSONDecodeError:
            pass
    
    # Update context with request context
    if request.context:
        context.update(request.context)
    
    # Load user's LLM configuration
    await llm_service.load_user_configuration(request.user_id)
    
    # Process through supervisor agent
    supervisor = get_supervisor_agent()
    agent_input = {
        "message": request.message,
        "user_id": request.user_id,
        "chat_id": chat.id,
        "context": context
    }
    
    result = await supervisor.execute_with_logging(chat.id, agent_input)
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {result.get('error', 'Unknown error')}"
        )
    
    # Store assistant response
    agent_result = result["result"]
    assistant_message = Message(
        chat_id=chat.id,
        role=MessageRole.ASSISTANT,
        content=agent_result.get("response", ""),
        agent_used="supervisor",
        tool_calls=json.dumps(agent_result.get("agent_results", [])) if agent_result.get("agent_results") else None,
        meta_data=json.dumps({
            "agents_used": agent_result.get("agents_used", []),
            "execution_plan": agent_result.get("execution_plan", {})
        })
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    # Store in Redis runtime state (conversation buffer)
    await runtime_state.add_message_to_conversation(
        chat_id=chat.id,
        message={
            "id": assistant_message.id,
            "role": "assistant",
            "content": agent_result.get("response", ""),
            "agent_used": "supervisor",
            "timestamp": assistant_message.created_at.isoformat()
        }
    )
    
    # Cache the response in Redis
    cache_key = f"response:{hash(request.message + str(chat.id))}"
    await runtime_state.cache_response(
        cache_key=cache_key,
        response=agent_result.get("response", ""),
        ttl=3600  # 1 hour
    )
    
    # Update chat context
    chat.context = json.dumps(context)
    await db.commit()
    
    return AssistantResponse(
        response=agent_result.get("response", ""),
        agents_used=agent_result.get("agents_used", []),
        agent_results=agent_result.get("agent_results"),
        execution_plan=agent_result.get("execution_plan"),
        chat_id=chat.id,
        message_id=assistant_message.id
    )


@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a chat (soft delete)"""
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat.status = ChatStatus.DELETED
    await db.commit()
    
    return {"message": "Chat deleted successfully"}
