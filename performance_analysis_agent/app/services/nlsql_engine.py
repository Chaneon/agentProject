from llama_index.core import ServiceContext
from llama_index.core.indices.struct_store import NLSQLTableQueryEngine
from openai import OpenAI
from pandas.io.sql import SQLDatabase

from app.core.config import settings
from app.core.db import mysql_engine

"""
NL2SQL 引擎：使用 LlamaIndex 将自然语言转换为 SQL。
"""
class NL2SQLEngine:
    def __init__(self):
        # 获取 mysql 引擎（连接数据库）
        self.sql_engine = mysql_engine
        # 创建 SQLDatabase 对象，指定可用的表（需根据实际业务调整）
        self.sql_database = SQLDatabase(
            self.sql_engine,
            include_tables = ["financial_metrics", "deposit_accounts", "loan_accounts"]
        )
        # 配置 LLM（使用 OpenAI 兼容接口）
        llm = OpenAI(
            api_key = settings.AGNES_APP_KEY,
            base_url = settings.AGNES_BASE_URL,
            model = settings.AGNES_MODEL,
            temperature = settings.AGNES_TEMPERATURE,
        )
        service_context = ServiceContext.from_defaults(llm = llm)
        # 创建 NL2SQL 查询引擎
        self.query_engine = NLSQLTableQueryEngine(
            sql_database = self.sql_database,
            service_context = service_context,
            tables = ["financial_metrics", "deposit_accounts", "loan_accounts"]
        )

    def generate_sql(self, natural_language : str) -> str:
        """将自然语言转换为 SQL 语句"""
        response = self.query_engine.query(natural_language)
        # 从响应元数据中提取 SQL
        return response.metadata["sql_query"]