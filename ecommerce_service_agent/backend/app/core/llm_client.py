from openai import AsyncOpenAI
from typing import Optional, List, Dict

from app.core.config import settings
from app.utils.logger import log

"""
LLM 客户端 - 封装大模型调用
"""
class LLMClient:
    """LLM 客户端（异步单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        self.client = AsyncOpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_API_BASE)
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        log.info(f"LLM 客户端初始化完成，模型: {self.model}")

    async def chat(self, prompt: str, max_tokens: int = 2000,
                   temperature: Optional[float] = None) -> str:
        """单轮对话"""
        try:
            temp = temperature if temperature is not None else self.temperature
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            log.error(f"LLM 调用失败: {e}")
            return f"生成失败: {str(e)}"


llm_client = LLMClient()