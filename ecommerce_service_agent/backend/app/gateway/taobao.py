from typing import Dict
from datetime import datetime

from app.gateway.base import BaseAdapter, InternalMessage

"""
淘宝适配器 - 处理淘宝/千牛平台的消息格式

注意：实际对接需要淘宝开放平台的 API 凭证
"""
class TaobaoAdapter(BaseAdapter):
    """淘宝适配器"""

    async def to_internal(self, raw_message: Dict) -> InternalMessage:
        """
        将淘宝消息转换为内部格式

        淘宝消息格式示例：
        {
            "sender_id": "淘宝用户ID",
            "content": "你好",
            "msg_type": "text"
        }
        """
        user_id = raw_message.get("sender_id", "")
        content = raw_message.get("content", "")
        session_key = raw_message.get("session_key") or f"taobao:{user_id}"

        return InternalMessage(
            platform="taobao",
            user_id=user_id,
            session_id=session_key,
            content=content,
            timestamp=datetime.now(),
            extra=raw_message
        )

    async def to_platform(self, internal: InternalMessage, reply: str) -> Dict:
        """
        将内部回复转换为淘宝消息格式
        """
        return {
            "msg_type": "text",
            "content": reply,
            "to_user_id": internal.user_id,
            "timestamp": datetime.now().isoformat()
        }


taobao_adapter = TaobaoAdapter()