from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from agent.contract_agent import contract_agent
from utils.logger import default_logger
"""
合同审查 API
"""

router = APIRouter()

@router.post("/review")
async def review_contract(file: UploadFile = File(...), contract_name: Optional[str]=Form(None)):
    """
   合同审查接口
   - 上传合同文件（PDF/DOCX）
   - 返回风险分析、改进建议和完整报告
   """
    try:
        # 读取文件内容
        file_bytes = await file.read()
        filename = file.filename

        # 调用 Agent 进行审查
        result = await  contract_agent.review(file_bytes, filename)

        return {
            "sucess": True,
            "contract_name": contract_name or filename,
            "risk_level": result["risk_level"],
            "analysis": result["analysis"],
            "suggestions": result["suggestions"],
            "report": result["report"]
        }
    except Exception as e:
        default_logger(f"合同审查事变：{e}")
        raise HTTPException(status_code=500, detail=str(e))