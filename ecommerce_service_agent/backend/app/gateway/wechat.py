
from typing import Dict
from datetime import datetime

from app.gateway.base import BaseAdapter, InternalMessage

"""
企业微信适配器 - 处理企业微信的消息格式
"""
class WechatAdapter(BaseAdapter):
    """企业微信适配器"""

    async def to_internal(self, raw_message: Dict) -> InternalMessage:
        """
        将企业微信消息转换为内部格式

        企业微信消息格式示例：
        {
            "FromUserName": "用户ID",
            "Content": "你好",
            "MsgType": "text"
        }
        """
        user_id = raw_message.get("FromUserName", "")
        content = raw_message.get("Content", "")

        return InternalMessage(
            platform="wechat",
            user_id=user_id,
            session_id=f"wechat:{user_id}",
            content=content,
            timestamp=datetime.now(),
            extra=raw_message
        )

    async def to_platform(self, internal: InternalMessage, reply: str) -> Dict:
        """将内部回复转换为企业微信消息格式"""
        return {
            "ToUserName": internal.user_id,
            "FromUserName": "系统",
            "CreateTime": int(datetime.now().timestamp()),
            "MsgType": "text",
            "Content": reply
        }


wechat_adapter = WechatAdapter()