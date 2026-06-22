import json
from typing import Optional, Dict, List
import redis

from app.core.config import settings
from app.utils.logger import log

"""
Redis 客户端模块

功能：
1. 连接 Redis（与主系统共用）
2. 读取用户 Session
3. 存储短期记忆、工作记忆
4. 消息队列（人工转接）
"""
class RedisClient:
    """Redis 客户端封装（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        """初始化 Redis 连接"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        try:
            self.client.ping()
            log.info(f"Redis 连接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            log.error(f"Redis 连接失败: {e}")
            raise

    # ========== 基础 KV 操作 ==========
    def get(self, key: str) -> Optional[str]:
        return self.client.get(key)

    def set(self, key: str, value: str, ttl: int = None):
        if ttl:
            self.client.setex(key, ttl, value)
        else:
            self.client.set(key, value)

    def set_json(self, key: str, value: dict, ttl: int = None):
        self.set(key, json.dumps(value, ensure_ascii=False), ttl)

    def get_json(self, key: str) -> Optional[dict]:
        value = self.get(key)
        return json.loads(value) if value else None

    def delete(self, key: str):
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0

    # ========== 列表操作（短期记忆）==========
    def lpush(self, key: str, value: str):
        return self.client.lpush(key, value)

    def lrange(self, key: str, start: int, end: int) -> List[str]:
        return self.client.lrange(key, start, end)

    def ltrim(self, key: str, start: int, end: int):
        self.client.ltrim(key, start, end)

    # ========== 队列操作（人工转接）==========
    def rpush(self, key: str, value: str):
        return self.client.rpush(key, value)

    def lpop(self, key: str) -> Optional[str]:
        return self.client.lpop(key)

    def lrem(self, key: str, count: int, value: str):
        self.client.lrem(key, count, value)


redis_client = RedisClient()