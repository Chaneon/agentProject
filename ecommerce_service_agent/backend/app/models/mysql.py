
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
# ============================================================
# Agent 自己维护的表（会创建）
# ============================================================

"""
SQLAlchemy ORM 模型定义

表说明：
- Agent 自己维护的表：会话、消息、摘要、转接记录
- 主系统的表：只读映射（商品、FAQ），不创建、不修改
"""

class ChatSession(Base):
    """会话表 - Agent 自己维护"""
    __tablename__ = "chat_session"

    session_id = Column(String(64), primary_key=True, comment="会话ID")
    user_id = Column(String(64), nullable=False, comment="用户ID")
    platform = Column(String(20), nullable=False, comment="平台来源")
    status = Column(Enum('active', 'closed', 'transferred'), default='active', comment="会话状态")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class ChatMessage(Base):
    """消息表 - Agent 自己维护"""
    __tablename__ = "chat_message"

    message_id = Column(Integer, primary_key=True, autoincrement=True, comment="消息ID")
    session_id = Column(String(64), nullable=False, comment="会话ID")
    role = Column(Enum('user', 'assistant', 'agent'), nullable=False, comment="消息角色")
    content = Column(Text, nullable=False, comment="消息内容")
    intent = Column(String(20), comment="识别出的意图")
    emotion = Column(String(20), comment="识别出的情绪")
    created_at = Column(DateTime, server_default=func.now(), comment="发送时间")


class ConversationSummary(Base):
    """对话摘要表 - 用于长期记忆RAG"""
    __tablename__ = "conversation_summary"

    summary_id = Column(Integer, primary_key=True, autoincrement=True, comment="摘要ID")
    user_id = Column(String(64), nullable=False, comment="用户ID")
    session_id = Column(String(64), nullable=False, comment="会话ID")
    summary_text = Column(Text, comment="摘要内容")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")


class TransferRecord(Base):
    """人工转接记录表"""
    __tablename__ = "transfer_record"

    transfer_id = Column(Integer, primary_key=True, autoincrement=True, comment="转接记录ID")
    session_id = Column(String(64), nullable=False, comment="会话ID")
    agent_id = Column(String(64), nullable=False, comment="接手的客服ID")
    reason = Column(String(100), comment="转接原因")
    context = Column(JSON, comment="对话上下文")
    created_at = Column(DateTime, server_default=func.now(), comment="转接时间")
    resolved_at = Column(DateTime, comment="解决时间")


# ============================================================
# 主系统表的只读映射（不创建表，只用于读取）
# ============================================================

class Product(Base):
    """商品表 - 映射主系统的表（只读）"""
    __tablename__ = "product"
    __table_args__ = {'autoload_with': None, 'extend_existing': True}

    product_id = Column(Integer, primary_key=True)
    sku = Column(String(100))
    name = Column(String(200))
    price = Column(Integer)
    category = Column(String(50))
    specs = Column(Text)
    selling_points = Column(Text)
    stock = Column(Integer)
    enabled = Column(Boolean)


class Faq(Base):
    """FAQ表 - 映射主系统的表（只读）"""
    __tablename__ = "faq"
    __table_args__ = {'autoload_with': None, 'extend_existing': True}

    faq_id = Column(Integer, primary_key=True)
    question = Column(String(500))
    answer = Column(Text)
    category = Column(String(50))
    keywords = Column(JSON)
    enabled = Column(Boolean)