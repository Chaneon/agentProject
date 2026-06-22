
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.schemas import ApiResponse
from app.models.mysql import ChatSession, ChatMessage
from app.core.database import get_db
"""
运营统计 API 路由
"""
router = APIRouter(prefix="/statistics", tags=["运营统计"])


@router.get("/dashboard", response_model=ApiResponse)
async def get_dashboard(
        request: Request,
        days: int = 30,
        db: Session = Depends(get_db)
):
    """运营看板数据"""
    user_info = getattr(request.state, "user_info", None)
    if not user_info or user_info.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    cutoff = datetime.now() - timedelta(days=days)

    total = db.query(ChatSession).filter(ChatSession.created_at >= cutoff).count()
    transferred = db.query(ChatSession).filter(
        ChatSession.created_at >= cutoff,
        ChatSession.status == "transferred"
    ).count()

    transfer_rate = round(transferred / total * 100, 2) if total > 0 else 0

    return ApiResponse.success({
        "total_sessions": total,
        "transfer_rate": transfer_rate,
        "avg_response_time": 2.5
    })


@router.get("/intent", response_model=ApiResponse)
async def get_intent_stats(
        request: Request,
        days: int = 30,
        db: Session = Depends(get_db)
):
    """意图分布统计"""
    user_info = getattr(request.state, "user_info", None)
    if not user_info or user_info.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    cutoff = datetime.now() - timedelta(days=days)

    messages = db.query(ChatMessage).filter(
        ChatMessage.created_at >= cutoff,
        ChatMessage.intent.isnot(None)
    ).all()

    stats = {"pre_sale": 0, "after_sale": 0, "chitchat": 0, "transfer": 0}
    for msg in messages:
        if msg.intent in stats:
            stats[msg.intent] += 1

    return ApiResponse.success(stats)


@router.get("/emotion", response_model=ApiResponse)
async def get_emotion_stats(
        request: Request,
        days: int = 30,
        db: Session = Depends(get_db)
):
    """情绪分布统计"""
    user_info = getattr(request.state, "user_info", None)
    if not user_info or user_info.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    cutoff = datetime.now() - timedelta(days=days)

    messages = db.query(ChatMessage).filter(
        ChatMessage.created_at >= cutoff,
        ChatMessage.emotion.isnot(None)
    ).all()

    stats = {"positive": 0, "neutral": 0, "negative": 0, "angry": 0}
    for msg in messages:
        if msg.emotion in stats:
            stats[msg.emotion] += 1

    return ApiResponse.success(stats)