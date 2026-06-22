import json
from typing import Optional, Dict

from app.core.redis_client import redis_client
from app.core.config import settings
from app.utils.logger import log

"""
转接服务 - 人工转接队列管理
"""
class TransferService:
    """转接服务类"""

    QUEUE_KEY = settings.TRANSFER_QUEUE_KEY

    @classmethod
    async def add_to_queue(cls, session_id: str, user_id: str, reason: str) -> int:
        item = json.dumps({"session_id": session_id, "user_id": user_id, "reason": reason})
        redis_client.rpush(cls.QUEUE_KEY, item)
        position = redis_client.llen(cls.QUEUE_KEY)
        log.info(f"会话加入转接队列: {session_id[:8]}..., position={position}")
        return position

    @classmethod
    async def get_next(cls) -> Optional[Dict]:
        item = redis_client.lpop(cls.QUEUE_KEY)
        return json.loads(item) if item else None


transfer_service = TransferService()