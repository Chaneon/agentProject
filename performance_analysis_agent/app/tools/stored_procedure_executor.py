from typing import Optional, Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_mysql_session
from app.utils.logger import default_logger
"""
存储过程执行器：
- 使用 SQLAlchemy 调用 MySQL 存储过程
- 支持位置参数
- 返回结果集（列名+行数据）
"""

class StoredProcedureExecutor:
    def __init__(self, db_session: Optional[Session]=None):
        self.db_session = db_session or get_mysql_session()

    def call_procedure(self, proc_name: str, params: List[Any])->Dict[str, Any]:
        """
        调用存储过程
        :param proc_name: 存储过程名称
        :param params: 位置参数列表，例如 [123, "2025-03-31", 10]
        :return: 包含 columns, rows, row_count 的字典
        """
        # 构造 CALL 语句，使用 %s 占位符
        placeholders = ','.join(['%s'] * len(params))
        call_sql = f"call {proc_name}({placeholders})"
        default_logger.info(f"执行存储过程：{call_sql}, 参数：{params}")

        try:
            # 执行 CALL
            result = self.db_session.execute(text(call_sql), params)
            rows = []
            columns = []
            # 获取结果集（如果存储过程返回 SELECT）
            if result.return_rows:
                columns = list(result.keys()) # 列名列表
                rows = [list(row) for row in result.fetchall()]
            self.db_session.commit()
            return {"columns":columns, "rows": rows, "row_count": len(rows)}
        except Exception as e:
            self.db_session.rollback()
            raise RuntimeError(f"执行存储过程执行失败：{str(e)}")

    def close(self):
        """关闭数据库会话"""
        self.db_session.close()
