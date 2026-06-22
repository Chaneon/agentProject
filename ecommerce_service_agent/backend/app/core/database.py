from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings
from app.utils.logger import log

"""
数据库连接模块 - 管理 MySQL 连接池

说明：
- Agent 连接主系统的 MySQL 数据库（只读）
- 不创建或修改主系统的表
- 只用于读取商品、FAQ 等数据
"""

# ============================================================
# 创建数据库引擎（连接主系统数据库）
# ============================================================
engine = create_engine(
    settings.mysql_url,
    pool_size=5,            # Agent 只需要少量连接
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    pool_recycle=3600,
)

# ============================================================
# 会话工厂
# ============================================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================
# ORM 基类
# ============================================================
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话（用于依赖注入）"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """初始化 Agent 自己的表（会话、消息等）"""
    try:
        # 只创建 Agent 自己的表，不创建主系统的表
        from app.models.mysql import ChatSession, ChatMessage, ConversationSummary, TransferRecord
        Base.metadata.create_all(bind=engine)
        log.info("Agent 数据库表初始化完成")
    except Exception as e:
        log.error(f"数据库初始化失败: {e}")
        raise