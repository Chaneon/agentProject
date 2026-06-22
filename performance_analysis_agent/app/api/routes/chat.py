import json
from datetime import datetime
from http.client import HTTPException
from typing import Dict
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.agents.router import AgentRouter
from app.api.depends import get_current_user
from app.core.db import get_mysql_session
from app.models.mysql import ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse

"""
统一对话路由：接收用户自然语言消息，通过 LangGraph 路由到对应 Agent，
保存对话历史，返回最终回复。
"""
router = APIRouter(prefix="/chat", tags=["统一对话"])

# 全局 Agent 路由器单例（复用，避免重复构建 LangGraph）
agent_router = None

def get_agent_router()->AgentRouter:
    global agent_router
    if agent_router is None:
        agent_router = AgentRouter()
    return agent_router

@router.post("/completions", response_model = ChatResponse)
async def chat_completions(req: ChatRequest,
                           user_info:Dict= Depends(get_current_user()),
                           db:Session = Depends(get_mysql_session()),
                           router_agent: AgentRouter= Depends(get_agent_router())):
    """
    统一对话接口。
    - 接收 session_id 和 message
    - 保存用户消息到数据库
    - 调用 AgentRouter 进行意图识别和分发
    - 保存助手回复
    - 返回结果
    """
    session_id = req.session_id
    user_id = user_info["user_id"]
    # --- 1. 确保会话存在（若无则创建）---
    chat_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not chat_session:
        chat_session = ChatSession(
            session_id = session_id,
            user_id = user_id,
            title = req.message[:50] # 取前50字作为会话标题
        )
        db.add(chat_session)
        db.commit()
    # --- 2. 保存用户消息 ---
    user_msg = ChatMessage(
            session_id = session_id,
            role = "user",
            content = req.message,
            created_at = datetime.now()
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    # --- 3. 调用 AgentRouter 处理 ---
    try:
        result = await router_agent.route(
            message = req.message,
            user_info = user_info,
            session_id = session_id,
            stream = req.steam
        )
        # result 包含 agent_type, reply, extra 等字段

        # --- 4. 保存助手回复 ---
        assistant_msg = ChatMessage(
            session_id = session_id,
            role = "assistant",
            agent_type = result.get("agent_type"),
            content = result.get("reply", ""),
            extra_data = json.dumps(result.get("extra", {})),
            created_at = datetime.now()
        )
        db.add(assistant_msg)
        db.commit()
        # --- 5. 返回成功响应 ---
        return ChatResponse(
            code = 200,
            data={
                "message_id": assistant_msg.message_id,
                "reply": result.get("reply"),
                "agent_used": result.get("agent_type"),
                "extra": result.get("extra", {})
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code = 500, detail = f"处理失败：{str(e)}")
