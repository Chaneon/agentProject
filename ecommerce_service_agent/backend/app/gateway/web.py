from typing import Dict
from datetime import datetime

from app.gateway.base import BaseAdapter, InternalMessage

"""
网页适配器 - 处理网页在线客服的消息格式

功能：
- 将网页聊天框的消息转换为内部统一格式
- 将内部回复转换为网页格式

请求格式：
{
    "user_id": "user_123",
    "message": "你好",
    "session_id": "optional"
}
"""
class WebAdapter(BaseAdapter):
    """网页适配器"""

    async def to_internal(self, raw_message: Dict) -> InternalMessage:
        """
        将网页消息转换为内部格式
        """
        user_id = raw_message.get("user_id", "")
        content = raw_message.get("message", "")
        session_id = raw_message.get("session_id") or f"web:{user_id}"

        return InternalMessage(
            platform="web",
            user_id=user_id,
            session_id=session_id,
            content=content,
            timestamp=datetime.now(),
            extra=raw_message
        )

    async def to_platform(self, internal: InternalMessage, reply: str) -> Dict:
        """
        将内部回复转换为网页消息格式
        """
        return {
            "session_id": internal.session_id,
            "reply": reply,
            "timestamp": datetime.now().isoformat(),
            "platform": "web"
        }


web_adapter = WebAdapter()