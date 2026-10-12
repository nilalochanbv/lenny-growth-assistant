import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    provider = Column(String(50), nullable=False, default="local")
    model_name = Column(String(100), nullable=False, default="qwen2.5:0.5b")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")
    artifacts = relationship("Artifact", back_populates="session", cascade="all, delete-orphan", order_by="Artifact.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    skill = Column(String(50), nullable=True)  # "knowledge_qa", "ship30_writer", "artifact_generator"
    citations = Column(JSON, nullable=True, default=list)  # list of citation objects
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="messages")


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(36), primary_key=True)
    doc_id = Column(String(255), nullable=False, index=True)
    doc_title = Column(String(255), nullable=False)
    doc_url = Column(String(500), nullable=False)
    doc_type = Column(String(50), nullable=False, default="podcast")
    guest = Column(String(255), nullable=True)
    date = Column(String(50), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    speaker = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True)  # list of floats
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    format = Column(String(20), nullable=False)  # "markdown" or "html"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    session = relationship("Session", back_populates="artifacts")
