from sqlalchemy import Column, Integer, String, JSON, Text, DateTime, func
from .user import Base


class ReportTask(Base):
    """报表任务表"""
    __tablename__ = "report_task"
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    report_name = Column(String(200), nullable=False)
    report_params = Column(JSON)          # 存储生成参数
    content_preview = Column(Text)        # 报表预览内容（如HTML）
    status = Column(Integer, default=0)   # 0:处理中, 1:成功, 2:失败
    java_report_id = Column(Integer, nullable=True)  # 同步到Java报表系统的ID
    created_at = Column(DateTime, server_default=func.now())