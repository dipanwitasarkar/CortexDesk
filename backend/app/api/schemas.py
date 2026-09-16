from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class MessageCreate(BaseModel):
    role: str
    content: str
    agent_used: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    meta_data: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    agent_used: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    @field_validator('tool_calls', mode='before')
    @classmethod
    def parse_tool_calls(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except:
                return None
        return v

    @field_validator('meta_data', mode='before')
    @classmethod
    def parse_meta_data(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except:
                return None
        return v

    class Config:
        from_attributes = True


class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"
    user_id: int
    context: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    id: int
    user_id: int
    title: str
    status: str
    context: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('context', mode='before')
    @classmethod
    def parse_context(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except:
                return None
        return v

    @field_validator('meta_data', mode='before')
    @classmethod
    def parse_meta_data(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except:
                return None
        return v

    class Config:
        from_attributes = True


class ChatWithMessages(ChatResponse):
    messages: List[MessageResponse]


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AssistantRequest(BaseModel):
    message: str
    user_id: int
    chat_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = None
    stream: bool = False


class AssistantResponse(BaseModel):
    response: str
    agents_used: List[str]
    agent_results: Optional[List[Dict[str, Any]]] = None
    execution_plan: Optional[Dict[str, Any]] = None
    chat_id: int
    message_id: int


class DocumentCreate(BaseModel):
    title: str
    file_type: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    title: str
    file_type: str
    content: Optional[str] = None
    file_path: Optional[str] = None
    chunk_count: int
    embedding_status: str
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('meta_data', mode='before')
    @classmethod
    def parse_meta_data(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except:
                return None
        return v

    class Config:
        from_attributes = True


class MemoryCreate(BaseModel):
    memory_type: str
    content: str
    importance: float = 0.5
    source: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    id: int
    user_id: int
    memory_type: str
    content: str
    importance: float
    source: Optional[str] = None
    embedding_id: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('meta_data', mode='before')
    @classmethod
    def parse_meta_data(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except:
                return None
        return v

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
