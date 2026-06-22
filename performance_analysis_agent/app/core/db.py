from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from redis import Redis
from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType
from app.core.config import settings
from app.utils.logger import default_logger

"""
数据库连接池模块：
- MySQL（SQLAlchemy 连接池）
- Redis（单例连接）
- Milvus（连接 + 集合管理）
"""

# 全局变量
mysql_engine = None
mysql_session_local = None
redis_client = None
milvus_knowledge_collection = None
milvus_procedure_collection = None

def init_mysql():
    """初始化 MySQL 连接池"""
    global mysql_engine, mysql_session_local
    mysql_url = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}?charset=utf8mb4"
    mysql_engine = create_engine(
        mysql_url,
        pool_size=10,          # 连接池大小
        max_overflow=20,       # 最大溢出连接数
        pool_pre_ping=True,    # 连接前检测是否可用
        echo=settings.DEBUG    # 是否打印SQL日志
    )
    mysql_session_local = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)
    default_logger.info("MySQL 连接池初始化完成")

def get_mysql_session() -> Session:
    """获取一个新的 MySQL 会话（用于请求内使用）"""
    if mysql_session_local is None:
        init_mysql()
    return mysql_session_local()

def init_redis():
    """初始化 Redis 连接"""
    global redis_client
    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        decode_responses=True   # 自动将响应解码为字符串
    )
    default_logger.info("Redis 连接初始化完成")
    return redis_client

def get_redis() -> Redis:
    """获取 Redis 客户端实例"""
    if redis_client is None:
        init_redis()
    return redis_client

def init_milvus():
    """
    初始化 Milvus 连接，并创建集合（如果不存在）。
    两个集合：
    - knowledge_base: 存储知识库文档片段
    - stored_procedures: 存储存储过程定义文档
    注意：索引类型使用 IVF_FLAT，度量类型使用 IP（内积），因为后续会对向量进行 L2 归一化。
    """
    global milvus_knowledge_collection, milvus_procedure_collection
    # 连接到 Milvus
    connections.connect(
        alias="default",
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT
    )
    default_logger.info("已连接到 Milvus")

    # --- 创建/加载知识库集合 ---
    if not utility.has_collection(settings.MILVUS_KNOWLEDGE_COLLECTION):
        # 定义集合 schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),  # 向量维度取决于模型
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, description="知识库文档向量集合")
        milvus_knowledge_collection = Collection(settings.MILVUS_KNOWLEDGE_COLLECTION, schema)
        # 创建索引（使用内积度量，要求向量归一化）
        index_params = {
            "metric_type": "IP",          # 内积，归一化后等价于余弦相似度
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        milvus_knowledge_collection.create_index("embedding", index_params)
        default_logger.info(f"创建集合 {settings.MILVUS_KNOWLEDGE_COLLECTION}")
    else:
        milvus_knowledge_collection = Collection(settings.MILVUS_KNOWLEDGE_COLLECTION)
        milvus_knowledge_collection.load()  # 加载到内存

    # --- 创建/加载存储过程集合 ---
    if not utility.has_collection(settings.MILVUS_PROCEDURE_COLLECTION):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="proc_name", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, description="存储过程定义集合")
        milvus_procedure_collection = Collection(settings.MILVUS_PROCEDURE_COLLECTION, schema)
        index_params = {"metric_type": "IP", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
        milvus_procedure_collection.create_index("embedding", index_params)
        default_logger.info(f"创建集合 {settings.MILVUS_PROCEDURE_COLLECTION}")
    else:
        milvus_procedure_collection = Collection(settings.MILVUS_PROCEDURE_COLLECTION)
        milvus_procedure_collection.load()

    default_logger.info("Milvus 初始化完成")

def get_milvus_knowledge_collection() -> Collection:
    """获取知识库集合"""
    if milvus_knowledge_collection is None:
        init_milvus()
    return milvus_knowledge_collection

def get_milvus_procedure_collection() -> Collection:
    """获取存储过程定义集合"""
    if milvus_procedure_collection is None:
        init_milvus()
    return milvus_procedure_collection