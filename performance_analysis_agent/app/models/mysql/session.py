from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON, Enum
from .user import Base

class ChatSession(Base):
    """对话会话表"""
    __tablename__ = "chat_session"
    session_id = Column(String(64), primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String(200))            # 会话标题
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class ChatMessage(Base):
    """对话消息表"""
    __tablename__ = "chat_message"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False)
    role = Column(Enum("user", "assistant", "system"), nullable=False)
    agent_type = Column(Enum("qa", "simulation", "report", "knowledge"))
    content = Column(Text)
    extra_data = Column(JSON)        # 存储附加信息（SQL、参数等）
    created_at = Column(DateTime, server_default=func.now())