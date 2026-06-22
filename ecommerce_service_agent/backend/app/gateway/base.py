from abc import ABC, abstractmethod
from typing import Dict
from dataclasses import dataclass
from datetime import datetime

"""
网关适配器基类 - 定义统一接口
"""
@dataclass
class InternalMessage:
    """内部统一消息格式"""
    platform: str
    user_id: str
    session_id: str
    content: str
    timestamp: datetime
    extra: Dict = None


class BaseAdapter(ABC):
    """适配器基类"""

    @abstractmethod
    async def to_internal(self, raw_message: Dict) -> InternalMessage:
        """转换为内部格式"""
        pass

    @abstractmethod
    async def to_platform(self, internal: InternalMessage, reply: str) -> Dict:
        """转换为平台格式"""
        pass