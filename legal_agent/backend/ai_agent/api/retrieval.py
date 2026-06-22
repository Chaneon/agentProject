from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent import research_agent
from utils.logger import default_logger
"""
法律检索 API
"""
router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.post("/search")
async def legal_search(request: SearchRequest):
    """
    法律检索接口
    - 输入自然语言查询
    - 返回法规、案例和分析报告
    """
    try:
        result = await research_agent.research(request.query)
        return {
            "success": True,
            "query": result["query"],
            "laws": result["laws"],
            "cases": result["cases"],
            "report": result["report"]
        }
    except Exception as e:
        default_logger.error(f"法律检索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))