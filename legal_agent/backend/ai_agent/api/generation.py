from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent import doc_agent
from utils.logger import default_logger

router = APIRouter()

class DocGenRequest(BaseModel):
    doc_type: str      # 起诉状/答辩状/律师函/合同
    facts: str
    claims: Optional[str] = None

@router.post("/generate")
async def generate_document(request: DocGenRequest):
    """
    文书生成接口
    - doc_type: 文书类型
    - facts: 案件事实
    - claims: 诉讼请求（可选）
    """
    try:
        result = await doc_agent.generate(request.doc_type, request.facts, request.claims)
        return {
            "success": True,
            "doc_type": result["doc_type"],
            "content": result["content"]
        }
    except Exception as e:
        default_logger.error(f"文书生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))