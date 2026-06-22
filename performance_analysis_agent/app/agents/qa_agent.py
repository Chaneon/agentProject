import json
from typing import Dict, Any
from app.core.db import get_redis, get_mysql_session
from app.core.security import SecurityManager
from app.services.llm_factory import LLMFactory
from app.services.nlsql_engine import NL2SQLEngine
from app.tools.sql_executor import SQLExecutor

"""
智能问答 Agent：
- 使用 LlamaIndex 将自然语言转为 SQL
- 通过安全执行器执行 SQL（自动添加机构过滤）
- 使用 LLM 将查询结果转换为自然语言回复
"""
class QAAgent:
    def __init__(self):
        # NL2SQL 引擎（使用 LlamaIndex）
        self.nl2sql_engine = NL2SQLEngine()
        # 安全管理器（用于权限过滤）
        redis_client = get_redis()
        db_session = get_mysql_session()
        self.security = SecurityManager(redis_client, db_session)
        # SQL 安全执行器
        self.sql_executor = SQLExecutor(self.security)
        # LLM 工厂（用于生成自然语言回复）
        self.llm = LLMFactory

    def build_prompt(self, question: str, rows: list) -> str:
        """构建用于生成自然语言回复的提示词"""
        return f"""根据用户问题：{question}
                    查询结果（JSON格式）：
                    {json.dumps(rows, ensure_ascii=False, indent=2)}
                    请用简洁的语句回答用户的问题。如果结果包含多个数值，可以适当总结。
                """

    async def process(self, message: str, user_info: Dict) -> Dict[str, Any]:
        """
       处理用户自然语言查询：
       1. 生成 SQL
       2. 执行 SQL（自动添加机构权限）
       3. 将结果转为自然语言
       """
        try:
            # 1. 生成 SQL
            sql = self.nl2sql_engine.generate_sql(message)
            # 2. 安全执行 SQL（自动添加 org_id 条件）
            rows = self.sql_executor.execute_sql(sql, user_info)
            # 3. 将结果转换为自然语言
            if not rows:
                reply = "未查询到相关数据"
            else:
                # 构建提示词，让 LLM 生成简洁的回答
                prompt = self.build_prompt(message, rows)
                reply = await self.llm.complete(prompt, max_tokens=300)
            return {"reply": reply, "extra": {"sql": sql, "row_count":len(rows)}}
        except Exception as e:
            return {"reply": f"查询失败：{str(e)}", "extra": {"error": str(e)}}
