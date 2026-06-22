from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.core.db import get_mysql_session
from app.models.mysql import ReportTask

"""
报表管理工具：
- 插入报表任务记录
- 更新任务状态和预览内容
"""
class ReportWriter:
    def __init__(self):
        self.db_session:Session = get_mysql_session()

    def create_report_task(self, user_id: int, report_name: str, report_params: Dict, content_preview: str)-> int:
        """
        创建新的报表任务记录
        :return: 任务ID (task_id)
        """
        task = ReportTask(
            user_id = user_id,
            report_name  = report_name,
            report_params = report_params,
            content_preview = content_preview,
            status = 0      # 0: 处理中
        )

        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)
        return task.task_id

    def update_task(self, task_id: int, status:int, content_preview:Optional[str] =None):
        """
        更新任务状态
        :param status: 0-处理中, 1-成功, 2-失败
        :param content_preview: 可选的预览内容（如 HTML）
        """
        task = self.db_session.query(ReportTask).filter(ReportTask.task_id == task_id).first()
        if task:
            task.status = status
            if content_preview is not None:
                task.content_preview = content_preview
            self.db_session.commit()

    def close(self):
        self.db_session.close()