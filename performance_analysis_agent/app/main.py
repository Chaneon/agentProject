from contextlib import asynccontextmanager
from sys import prefix

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.depends import init_security_manager
from app.api.routes import chat, simulation, knowledge, report
from app.core.db import init_mysql, init_redis, init_milvus
from app.utils.logger import default_logger

"""
FastAPI 应用入口
配置生命周期、CORS、路由注册
"""
#asynccontextmanager 是 Python 中用于创建异步上下文管理器的装饰器.管理资源的获取和释放
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
   应用生命周期管理器（替代旧的 on_event）
   在启动时初始化所有资源，在关闭时清理
   """
    default_logger.info("正在启动应用...")
    # 初始化数据库连接池
    init_mysql()
    # 初始化 Redis 连接
    init_redis()
    # 初始化 Milvus 连接和集合
    init_milvus()
    # 初始化安全管理器（依赖 Redis 和 MySQL）
    init_security_manager()
    default_logger.info("应用启动完成")
    # 此处应用运行. yield让一个函数可以“暂停执行、返回一个值、然后从暂停的地方继续”，而不是像普通函数那样一次性执行完并返回
    yield
    default_logger.info("正在关闭应用...")
    # 可以在这里添加关闭连接的逻辑

def create_app()->FastAPI:
    """创建 FastAPI 实例并配置路由"""
    app = FastAPI(
        title = "银行经营分析智能体",
        description = "基于LLM的智能经营分析助手，支持NL2SQL、模拟测算、报告生成、知识库问答",
        version = "1.0.0",
        lifespan = lifespan
    )
    # 配置 CORS 跨域，允许前端直接调用
    app.add_middleware(
        CORSMiddleware,
        allow_origin = ["*"],        # 生产环境应指定具体域名
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"]
    )

    # 注册各个路由模块，统一前缀 /api
    prefix = "/api"
    app.include_router(chat.router, prefix = prefix)
    app.include_router(simulation.router, prefix = prefix)
    app.include_router(report.router, prefix = prefix)
    app.include_router(knowledge.router, prefix = prefix)


# 创建全局 app 实例，供 uvicorn 使用
app = create_app()