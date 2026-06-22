from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api import chat, statistics
from app.core.database import Base, engine
from app.core.redis_client import redis_client
from app.core.milvus_client import milvus_client
from app.core.auth import get_user_from_session
from app.utils.logger import log

"""
电商智能客服Agent - FastAPI 应用主入口

功能：
1. 创建 FastAPI 应用实例
2. 配置 CORS 跨域
3. 注册 API 路由
4. 添加认证中间件
5. 生命周期管理
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理器"""
    log.info("正在启动电商智能客服系统...")

    # 创建Agent自己的表（会话、消息等）
    Base.metadata.create_all(bind=engine)
    log.info("Agent数据库表初始化完成")

    # 测试 Redis 连接
    try:
        redis_client.client.ping()
        log.info("Redis 连接正常")
    except Exception as e:
        log.warning(f"Redis 连接失败: {e}")

    # 测试 Milvus 连接
    try:
        milvus_client.product_collection.load()
        log.info("Milvus 连接正常")
    except Exception as e:
        log.warning(f"Milvus 连接失败: {e}")

    yield

    log.info("正在关闭电商智能客服系统...")


app = FastAPI(
    title="电商智能客服Agent",
    description="独立部署的AI智能客服，支持多渠道接入",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """认证中间件：从X-Session-Id读取用户信息"""
    # 跳过健康检查
    if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    session_id = request.headers.get("X-Session-Id")
    if not session_id:
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "缺少会话标识 X-Session-Id"}
        )

    user_info = get_user_from_session(session_id)
    if not user_info:
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": "会话无效或已过期"}
        )

    request.state.user_info = user_info
    request.state.session_id = session_id
    request.state.user_id = user_info.get("user_id")

    response = await call_next(request)
    return response


# 注册路由
app.include_router(chat.router, prefix="/api/v1")
app.include_router(statistics.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "ecommerce-customer-service"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "电商智能客服Agent",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)