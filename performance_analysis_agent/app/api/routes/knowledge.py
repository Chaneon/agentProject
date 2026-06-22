import os.path
import shutil
from http.client import HTTPException
from typing import Dict

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.agents.knowledge_agent import KnowledgeAgent
from app.api.depends import get_current_user
from app.core.db import get_mysql_session
from app.models.schemas import KnowledgeAskRequest, KnowledgeAskResponse
from app.utils.logger import default_logger
"""
知识库管理接口：
- 问答：用户提问，RAG检索 + LLM生成答案
- 上传：上传文档（PDF/Word/TXT），解析并存入 Milvus（简化版）
"""
router = APIRouter(prefix="/knowledge", tags = ["知识库"])

@router.post("/ask", response_model=KnowledgeAskResponse)
def ask_knowledge(
        req: KnowledgeAskRequest,
        user_info:Dict= Depends(get_current_user())):
    """
   知识库问答：
   - 使用 KnowledgeAgent 进行双路召回+重排+LLM生成
   - 返回答案和引用来源（文档ID）
   """
    agent = KnowledgeAgent(user_info)
    answer, sources = agent.answer_question(req.question)
    return KnowledgeAskResponse(answer = answer, sources = sources)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), user_info:Dict= Depends(get_current_user())):
    """
    上传文档到知识库：
    - 将文件临时保存到 /tmp 目录
    - 调用文档加载服务（实际需实现解析、分块、向量化、存入Milvus）
    - 此处仅做示例，打印日志并返回虚拟 doc_id
    """
    # 安全处理文件名，防止路径遍历
    safe_filename = os.path.basename(file.filename)
    temp_path = f"/tmp/{safe_filename}"
    try:
        # 将上传的文件内容写入临时文件
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # 记录日志（实际应调用解析服务）
        default_logger.info(f"上传文件：{safe_filename}，用户：{user_info["user_id"]}")
        # 生成虚拟文档ID（实际应由解析服务返回）
        doc_id = f"doc_{safe_filename.replace('.', '_')}"
        # 删除临时文件
        os.remove(temp_path)
        return {"doc_id": doc_id, "message": "上传成功，正在处理中..."}
    except Exception as e:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code = 500, detail = str(e))
