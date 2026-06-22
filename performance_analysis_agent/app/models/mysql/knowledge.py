from sqlalchemy import Column, Integer, String, DateTime, func, SmallInteger
from .user import Base

class KnowledgeDocument(Base):
    """知识库文档元数据表"""
    __tablename__ = "knowledge_document"
    doc_id = Column(String(64), primary_key=True)
    title = Column(String(200))
    category = Column(String(50))      # 分类：制度、指标口径等
    file_name = Column(String(200))
    upload_user_id = Column(Integer)
    status = Column(SmallInteger, default=0)  # 0:启用, 1:禁用
    created_at = Column(DateTime, server_default=func.now())