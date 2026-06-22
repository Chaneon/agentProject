import json
import re
from typing import Dict, Any
import pandas as pd
from redis.commands.search import result

from app.core.db import get_redis
from app.core.security import SecurityManager
from app.services.llm_factory import LLMFactory
from app.tools.report_writer import ReportWriter
from app.tools.sql_executor import SQLExecutor

"""
报告生成 Agent：
- 根据用户指令生成 SQL 查询数据
- 将结果格式化为报表预览
- 插入报表任务记录到数据库
- 支持异步执行
"""
class ReportAgent:
    def __init__(self, db_session=None, user_info: Dict = None):
        self.db_session = db_session
        self.user_info = user_info
        self.report_writer = ReportWriter() # 报表数据库操作工具
        self.llm = LLMFactory
        # 安全执行器（用于执行查询）
        redis_client = get_redis()
        self.security = SecurityManager(redis_client, db_session)
        self.sql_executor = SQLExecutor(self.security)

    def create_report_task(self, report_name: str, instruction: str) -> int:
        """创建报表任务记录，返回任务 ID"""
        return  self.report_writer.create_report_task(
            user_id= self.user_info['user_id'],
            report_name= report_name,
            report_params={"instruction": instruction},
            content_view = ""
        )

    async def generate_and_save(self, task_id: int, instruction: str, report_name: str):
        """
       后台执行报表生成：
       - 使用 LLM 将指令转换为 SQL
       - 执行 SQL 获取数据
       - 生成 HTML 预览
       - 更新任务状态
       """
        try:
            # 1. 生成 SQL
            sql_prompt = f"用户需要生成报表：{instruction}\n 生成对应的sql查询语句，只输出sql。"
            sql = await self.llm.complete(sql_prompt, max_tokens=300)
            sql = sql.strip().replace("```sql", "").replace("```", "")
            # 2. 执行查询（权限过滤）
            rows = self.sql_executor.execute_sql(sql, self.user_info)
            # 3. 生成预览（HTML表格）
            df = pd.DataFrame(rows)
            preview = df.head(10).to_html() if not df.empty else "无数据"
            # 4. 更新任务状态为成功，并保存预览内容
            self.report_writer.update_task(task_id, status=1, content_preview= preview)
        except Exception as e:
            # 更新任务状态为失败
            self.report_writer.update_task(task_id, status=2)
            raise e

    async def process(self, message: str)-> Dict[str, Any]:
        """
       同步处理入口（实际使用中建议通过后台任务调用 generate_and_save）
       此处简化：直接创建任务并等待完成（生产环境建议异步）
       """
        # 提取报表名称和指令
        prompt = f"从以下消息中提取报表名称和生成要求：{message}。输出JSON格式：{{'report_name':'xxx','instruction':'xxx'}}"
        result = await self.llm.complete(prompt, max_tokens=200)
        match = re.search(r"\[.*\]", result, re.DOTALL)
        if match:
            params = json.loads(match.group())
            report_name = params['report_name']
            instruction = params['instruction']
        else:
            report_name = "临时报表"
            instruction = message
            params = {"report_name":report_name, "instruction":instruction}
        # 创建任务
        task_id = self.create_report_task(report_name, params['instruction'])
        # 同步生成（实际应放入后台）
        await self.generate_and_save(task_id, report_name, instruction)

        return {"reply":"报表生成任务已提交，任务ID：{task_id}，请稍后再报表管理模块查看", "extra":{"task_id": task_id}}