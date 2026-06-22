from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import retrieval, generation, contract, health
from core.vector_store import init_milvus
from utils.logger import default_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时初始化 Milvus 连接"""
    default_logger.info("启动 Python 算法服务...")
    # 初始化 Milvus 连接
    init_milvus()
    default_logger.info("Milvus 连接初始化完成")
    yield
    default_logger.info("关闭服务...")

# 创建 FastAPI 实例
app = FastAPI(
    title="法律 AI 算法服务",
    description="提供合同审查、法律检索、文书生成等 AI 能力",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS，允许 SpringBoot 调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(contract.router, prefix="/api/contract", tags=["合同审查"])
app.include_router(retrieval.router, prefix="/api/legal", tags=["法律检索"])
app.include_router(generation.router, prefix="/api/doc", tags=["文书生成"])
app.include_router(health.router, prefix="/api", tags=["健康检查"])