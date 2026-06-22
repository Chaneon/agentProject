from sqlalchemy import Integer, Column, String
from sqlalchemy.ext.declarative import declarative_base

# Base 就像一个“模型注册中心”。你定义的每个数据表类，都要继承它，SQLAlchemy 才能知道这些类对应哪些数据库表。
Base = declarative_base()

class User(Base):
    """用户表（与Java系统共享，映射 sys_user）"""
    __tablename__ = "sys_user"
    user_id = Column(Integer, primary_key =True)
    user_name = Column(String(50))
    role = Column(String(20))
    org_id = Column(Integer)

class UserOrgVisibility(Base):
    """用户可见机构临时表（Agent系统专用）"""
    __tablename__ = "user_org_visibility"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    visible_org_id = Column(Integer, nullable=False)
