from sqlalchemy import Column, Integer, String, JSON, Numeric, DateTime, func
from .user import Base

class SimulationRecord(Base):
    """模拟测算记录表"""
    __tablename__ = "simulation_record"
    sim_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    assumption = Column(JSON)          # 假设条件
    target_metric = Column(String(100)) # 目标指标
    result_value = Column(Numeric(20,4))  # 测算结果
    baseline_value = Column(Numeric(20,4)) # 基准值（可选）
    created_at = Column(DateTime, server_default=func.now())