from pydantic import BaseModel, Field, validator
from typing import Optional, Any
"""
Pydantic 请求/响应模型
"""


# ============================================================
# 通用响应
# ============================================================
class ApiResponse(BaseModel):
    """统一 API 响应"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

    @classmethod
    def success(cls, data=None, message: str = "success"):
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, message: str, code: int = 500):
        return cls(code=code, message=message, data=None)


# ============================================================
# 对话相关
# ============================================================
class ChatSendRequest(BaseModel):
    """发送消息请求（网关统一格式）"""
    message: str = Field(..., min_length=1, max_length=2000)
    platform: str = Field(..., description="平台：taobao/douyin/wechat/web")
    user_id: Optional[str] = Field(None, description="平台用户ID")
    session_id: Optional[str] = Field(None, description="会话ID，不传则自动生成")

    @validator('message')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('消息内容不能为空')
        return v.strip()


class ChatSendResponse(BaseModel):
    """发送消息响应"""
    reply: str
    need_transfer: bool = False
    session_id: str


class TransferRequest(BaseModel):
    """转人工请求"""
    reason: Optional[str] = Field(None, max_length=200)


class TransferResponse(BaseModel):
    """转人工响应"""
    status: str
    queue_position: Optional[int] = None


# ============================================================
# 统计相关
# ============================================================
class DashboardResponse(BaseModel):
    """运营看板"""
    total_sessions: int
    transfer_rate: float
    avg_response_time: float


class IntentStatsResponse(BaseModel):
    """意图统计"""
    pre_sale: int = 0
    after_sale: int = 0
    chitchat: int = 0
    transfer: int = 0


class EmotionStatsResponse(BaseModel):
    """情绪统计"""
    positive: int = 0
    neutral: int = 0
    negative: int = 0
    angry: int = 0