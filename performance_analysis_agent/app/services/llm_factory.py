from openai import OpenAI
from app.core.config import settings
"""
LLM 工厂类：统一管理 LLM 调用。
支持 OpenAI 兼容接口（如 vLLM、Ollama、DeepSeek 等）。
"""
class LLMFactory:
    _client_ = None

    @classmethod
    def get_client(cls):
        """获取 OpenAI 客户端实例（单例）"""
        if cls._client_ is None:
            if settings.LLM_PROVIDER == "openai_compatible":
                cls._client_ = OpenAI(
                    api_key = settings.AGNES_APP_KEY,
                    base_url = settings.AGNES_BASE_URL
                )
            else:
                raise ValueError(f"Unsupported LLM provider:{settings.LLM_PROVIDER}")
        return cls._client_

    @classmethod
    async def complete(cls, prompt: str, max_tokens: int = 500) -> str:
        """
        调用 LLM 生成文本
        :param prompt: 提示词
        :param max_tokens: 最大生成 token 数
        :return: 生成的文本
        """
        client = cls.get_client();
        response = client.chat.completions.create(
            model = settings.AGNES_MODEL,
            messages = [{"role": "user", "content": prompt}],
            temperature = settings.AGNES_TEMPERATURE,
            max_tokens = max_tokens
        )
        return response.choices[0].message.content
