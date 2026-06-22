import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

"""
配置管理模块：从环境变量读取配置，提供全局配置对象。
使用 pydantic-settings 自动映射环境变量。
"""
# 加载 .env 文件
load_dotenv()

class Setting(BaseSettings):
    """ 应用配置类，属性名与.env的变量名一致"""
    # 应用基础配置
    APP_NAME: str = "BankAgentSystem"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LLM_PROVIDER:str = os.getenv("LLM_PROVIDER")

    # LLM 配置
    AGNES_APP_KEY:str = os.getenv("AGNES_APP_KEY")
    AGNES_APP_ID:str = os.getenv("AGNES_APP_ID")
    AGNES_BASE_URL:str = os.getenv("AGNES_BASE_URL")
    AGNES_MODEL:str = os.getenv("AGNES_MODEL")
    AGNES_TEMPERATURE:str = os.getenv("AGNES_TEMPERATURE")

    # MySQL 配置（与Java系统共用）
    MYSQL_HOST:str = os.getenv("MYSQL_HOST")
    MYSQL_PORT:str = os.getenv("MYSQL_PORT")
    MYSQL_USERNAME:str = os.getenv("MYSQL_USERNAME")
    MYSQL_PWD:str = os.getenv("MYSQL_PWD")
    MYSQL_DATABASE:str = os.getenv("MYSQL_DATABASE")

    # Redis 配置（与Java系统共用）
    REDIS_HOST:str = os.getenv("REDIS_HOST")
    REDIS_PORT:str = os.getenv("REDIS_PORT")
    REDIS_PWD:str = os.getenv("REDIS_PWD")
    REDIS_DB:str = os.getenv("REDIS_DB")

    # Milvus 配置
    MILVUS_HOST:str = os.getenv("MILVUS_HOST")
    MILVUS_PORT:str = os.getenv("MILVUS_PORT")
    MILVUS_KNOWLEGE_COLLECTION:str = os.getenv("MILVUS_KNOWLEGE_COLLECTION")
    MILVUS_PROCEDURE_COLLECTION:str = os.getenv("MILVUS_PROCEDURE_COLLECTION")

    # NL2SQL 执行限制
    SQL_EXECUTOR_TIMEOUT:str = os.getenv("SQL_EXECUTOR_TIMEOUT")
    SQL_MAX_ROW:str = os.getenv("SQL_MAX_ROW")

    # 重排模型（HuggingFace 模型名或路径）
    RERANK_MODEL:str = os.getenv("RERANK_MODEL")
    # 向量化模型（用于生成 embedding）
    EMBEDDING_MODEL:str = os.getenv("EMBEDDING_MODEL")

    # 角色常量（与Java系统保持一致）
    ROLE_MANAGER: str = "MANAGER"
    ROLE_BUSINESS: str = "BUSINESS"

settings = Setting()