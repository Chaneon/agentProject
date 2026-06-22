import json
from typing import List, Dict
from datetime import datetime

from app.core.redis_client import redis_client
from app.utils.logger import log

"""
记忆服务 - 短期记忆、工作记忆、长期记忆
"""
class MemoryService:
    """记忆服务类"""

    SHORT_TERM_KEY = "chat:short:{}"
    WORK_MEMORY_KEY = "chat:work:{}"
    TTL = 1800  # 30分钟
    MAX_MESSAGES = 20

    # ========== 短期记忆 ==========
    @classmethod
    def save_short_term(cls, session_id: str, role: str, content: str):
        key = cls.SHORT_TERM_KEY.format(session_id)
        messages = cls.get_short_term(session_id)
        messages.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        if len(messages) > cls.MAX_MESSAGES:
            messages = messages[-cls.MAX_MESSAGES:]
        redis_client.set_json(key, messages, cls.TTL)

    @classmethod
    def get_short_term(cls, session_id: str) -> List[Dict]:
        key = cls.SHORT_TERM_KEY.format(session_id)
        return redis_client.get_json(key) or []

    @classmethod
    def clear_short_term(cls, session_id: str):
        redis_client.delete(cls.SHORT_TERM_KEY.format(session_id))

    # ========== 工作记忆 ==========
    @classmethod
    def set_work_memory(cls, session_id: str, state: str, data: Dict = None):
        key = cls.WORK_MEMORY_KEY.format(session_id)
        work_memory = {"state": state, "data": data or {}, "updated_at": datetime.now().isoformat()}
        redis_client.set_json(key, work_memory, cls.TTL)

    @classmethod
    def get_work_memory(cls, session_id: str) -> Dict:
        key = cls.WORK_MEMORY_KEY.format(session_id)
        return redis_client.get_json(key) or {"state": "idle", "data": {}}

    @classmethod
    def clear_work_memory(cls, session_id: str):
        redis_client.delete(cls.WORK_MEMORY_KEY.format(session_id))


memory_service = MemoryService()