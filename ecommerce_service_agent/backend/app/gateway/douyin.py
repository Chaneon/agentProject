
from typing import Dict
from datetime import datetime

from app.gateway.base import BaseAdapter, InternalMessage

"""
抖音适配器 - 处理抖音/飞鸽平台的消息格式
"""
class DouyinAdapter(BaseAdapter):
    """抖音适配器"""

    async def to_internal(self, raw_message: Dict) -> InternalMessage:
        """
        将抖音消息转换为内部格式
        """
        user_id = raw_message.get("from_user_id", "")
        content = raw_message.get("content", "")

        return InternalMessage(
            platform="douyin",
            user_id=user_id,
            session_id=f"douyin:{user_id}",
            content=content,
            timestamp=datetime.now(),
            extra=raw_message
        )

    async def to_platform(self, internal: InternalMessage, reply: str) -> Dict:
        """将内部回复转换为抖音消息格式"""
        return {
            "msg_type": "text",
            "content": reply,
            "to_user_id": internal.user_id,
            "timestamp": datetime.now().isoformat()
        }


douyin_adapter = DouyinAdapter()