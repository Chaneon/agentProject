from typing import Optional, Dict

from app.core.redis_client import redis_client
from app.core.config import settings
from app.utils.logger import log

"""
认证模块 - 从 Redis 读取用户 Session
"""
def get_user_from_session(session_id: str) -> Optional[Dict]:
    """
    从 Redis 获取用户信息

    Redis Key 格式：session:{tokenId}
    主系统登录时写入此 Key
    """
    if not session_id:
        return None

    key = f"{settings.REDIS_SESSION_PREFIX}{session_id}"
    user_info = redis_client.get_json(key)

    if not user_info:
        log.warning(f"Session 不存在或已过期: {session_id[:8]}...")
        return None

    return user_info


def get_user_id_from_session(session_id: str) -> Optional[str]:
    user_info = get_user_from_session(session_id)
    return user_info.get("user_id") if user_info else None