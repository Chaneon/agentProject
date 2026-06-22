from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models.schemas import ApiResponse, ChatSendRequest, ChatSendResponse, TransferRequest
from app.services.chat_service import chat_service
from app.services.sync_service import sync_service
from app.core.database import get_db
from app.gateway.web import web_adapter
from app.gateway.taobao import taobao_adapter
from app.gateway.douyin import douyin_adapter
from app.gateway.wechat import wechat_adapter
from app.utils.logger import log
"""
对话 API 路由 - 统一消息入口

所有平台的消息都通过此接口进入Agent
"""
router = APIRouter(prefix="/chat", tags=["对话"])

# 平台适配器映射
adapters = {
    "web": web_adapter,
    "taobao": taobao_adapter,
    "douyin": douyin_adapter,
    "wechat": wechat_adapter,
}


@router.post("/send", response_model=ApiResponse)
async def send_message(
        request: Request,
        req: ChatSendRequest,
        db: Session = Depends(get_db)
):
    """
    统一消息发送接口

    请求头：
    - X-Session-Id: 主系统登录后的 tokenId

    请求体：
    - message: 消息内容
    - platform: 平台类型（web/taobao/douyin/wechat）
    - user_id: 平台用户ID（可选）
    - session_id: 会话ID（可选）

    返回：
    - reply: AI回复
    - need_transfer: 是否需要转人工
    - session_id: 会话ID
    """
    # 1. 获取用户信息
    user_info = getattr(request.state, "user_info", None)
    if not user_info:
        raise HTTPException(status_code=401, detail="未认证")

    user_id = user_info.get("user_id")

    # 2. 获取适配器
    adapter = adapters.get(req.platform)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"不支持的平台: {req.platform}")

    # 3. 转换为内部格式
    internal_msg = await adapter.to_internal({
        "user_id": req.user_id,
        "message": req.message,
        "session_id": req.session_id
    })

    # 4. 处理消息
    result = await chat_service.process_message(
        db=db,
        user_id=user_id,
        user_info=user_info,
        session_id=internal_msg.session_id,
        message=internal_msg.content,
        platform=req.platform
    )

    log.info(f"消息处理完成: user={user_id}, platform={req.platform}, session={result['session_id'][:8]}...")
    return ApiResponse.success(result)


@router.post("/transfer", response_model=ApiResponse)
async def transfer_to_human(
        request: Request,
        req: TransferRequest,
        db: Session = Depends(get_db)
):
    """主动转人工"""
    user_info = getattr(request.state, "user_info", None)
    if not user_info:
        raise HTTPException(status_code=401, detail="未认证")

    session_id = getattr(request.state, "session_id", None)
    user_id = user_info.get("user_id")

    result = await chat_service.transfer_to_human(db, session_id, user_id, req.reason)
    return ApiResponse.success(result)


@router.post("/sync/products", response_model=ApiResponse)
async def sync_products(
        request: Request,
        db: Session = Depends(get_db)
):
    """手动同步商品到向量库（需要管理员权限）"""
    user_info = getattr(request.state, "user_info", None)
    if not user_info or user_info.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    result = await sync_service.sync_products(db)
    return ApiResponse.success(result)


@router.post("/sync/faqs", response_model=ApiResponse)
async def sync_faqs(
        request: Request,
        db: Session = Depends(get_db)
):
    """手动同步FAQ到向量库（需要管理员权限）"""
    user_info = getattr(request.state, "user_info", None)
    if not user_info or user_info.get("role") != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")

    result = await sync_service.sync_faqs(db)
    return ApiResponse.success(result)