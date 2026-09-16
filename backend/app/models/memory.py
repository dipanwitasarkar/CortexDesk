from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class MemoryType(enum.Enum):
    PERSONAL = "personal"
    PROJECT = "project"
    PREFERENCE = "preference"
    KNOWLEDGE = "knowledge"
    WORK_JOURNAL = "work_journal"


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    memory_type = Column(Enum(MemoryType), nullable=False)
    content = Column(Text, nullable=False)
    importance = Column(Float, default=0.5)  # 0.0 to 1.0
    source = Column(String(100))  # Where this memory came from
    embedding_id = Column(String(100))  # Qdrant point ID
    meta_data = Column(Text)  # JSON string for additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="memories")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    input_prompt = Column(Text, nullable=False)
    output_response = Column(Text)
    execution_time = Column(Float)  # in seconds
    tool_calls = Column(Text)  # JSON string
    error_message = Column(Text)
    status = Column(String(50), default="completed")  # completed, failed, timeout
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("Chat", backref="agent_executions")


# Observability Models (PostgreSQL-based)
class ObservabilityMetric(Base):
    __tablename__ = "observability_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, timing
    tags = Column(JSON)  # Flexible tagging
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ObservabilityTrace(Base):
    __tablename__ = "observability_traces"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(100), nullable=False, index=True)
    parent_span_id = Column(String(100), nullable=True)
    span_id = Column(String(100), nullable=False)
    operation_name = Column(String(200), nullable=False)
    service_name = Column(String(100), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, nullable=True)
    status = Column(String(50), nullable=False)  # success, error, timeout
    meta_data = Column(JSON)  # Additional context
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class ObservabilityLog(Base):
    __tablename__ = "observability_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, DEBUG
    logger_name = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
