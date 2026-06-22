from typing import Dict, Any, List

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import result

from app.core.config import settings
from app.core.db import get_mysql_session
from app.core.security import SecurityManager
"""
安全 SQL 执行器：
- 自动添加机构权限过滤
- 只允许 SELECT 语句
- 设置超时和结果集行数限制
"""
class SQLExecutor:
    def __init__(self, security_manager: SecurityManager):
        self.security - security_manager

    def execute_sql(self,sql: str, user_info:Dict) -> List[Dict[str, Any]]:
        """
       执行查询 SQL 并返回结果列表（字典形式）
       - 自动注入 org_id 条件
       - 检查只读性
       - 设置超时
       - 限制返回行数
       """

        # 1. 权限过滤：添加 org_id 条件
        filtered_sql = self.security.apply_org_filter(user_info, sql)

        # 2. 安全检查：仅允许 SELECT
        if not self.is_readonly_query(filtered_sql):
            raise ValueError("只允许执行SELECT查询")
        # 3. 执行查询
        session = get_mysql_session()
        try:
            # 设置 MySQL 执行超时（单位毫秒）
            session.execute(text(f"set session max_execution_time = {settings.SQL_EXECUTOR_TIMEOUT * 1000}"))
            # 限制最大返回行数
            limited_sql = f"select * from ({filtered_sql}) as limited limit {settings.SQL_MAX_ROW}"
            result = session.execute(text(limited_sql))
            # 将结果转换为字典列表
            rows = result.mappings().all()
            return [dict(row) for row in rows]
        except SQLAlchemyError as e:
            raise  RuntimeError(f"SQL执行失败:{str(e)}")
        finally:
            session.close()



    def is_readonly_query(self, sql: str) ->bool:
        """检查SQL是否为select语句"""
        sql_upper = sql.strip().upper()
        # sql语句是否为select开头
        if not sql_upper.startswith("SELECT"):
            return False

        dangerous = ["UPDATE", "DELETE","DROP","ALTER", "INSTERT","CREATE", "TRUNCATE"]

        for kw in dangerous:
            if kw in sql_upper:
                return False
        # 简单防止多语句执行
        if ";" in sql_upper.rsplit(";"):
            return False

        return True