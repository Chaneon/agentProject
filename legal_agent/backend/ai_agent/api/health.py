from fastapi import APIRouter

from core.llm_client import llm_client
from core.vector_store import get_collection
from utils.logger import default_logger

router = APIRouter()

@router.get("/health")
async def health_check():
    """健康检查接口，用于 SpringBoot 探测服务状态"""
    try:
        # 检查 LLM 是否可用（简单测试）
        test_response = llm_client.chat("ping", max_tokens=5)
        # 检查 Milvus 是否可用
        collection = get_collection()
        return {
            "status": "healthy",
            "llm": "ok",
            "milvus": collection.name if collection else "error"
        }
    except Exception as e:
        default_logger.error(f"健康检查失败: {e}")
        return {"status": "unhealthy", "error": str(e)}