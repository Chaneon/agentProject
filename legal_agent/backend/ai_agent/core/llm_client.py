from openai import OpenAI
from models.config import settings
from utils.logger import default_logger

"""
大语言模型客户端封装（OpenAI 兼容接口）
"""
class LLMClient:
    """LLM 客户端单例"""
    _instance =None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = OpenAI(
                api_key = settings.llm_api_key,
                base_url = settings.llm_api_base
            )
            cls._instance.model = settings.llm_model
            cls._instance.temperature = settings.llm_temperature
            default_logger.info(f"LLM 客户端初始化完成，模型: {settings.llm_model}")
        return  cls._instance

    def chat(self, prompt: str, max_tokens: int = 2000, temperature: float = None) -> str:
        """调用 LLM 生成文本"""
        try:
            temp = temperature if temperature is not None else self.temperature
            response = self.client.chat.completions.create(
                model= self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature = temp,
                max_tokens = max_tokens

            )
            return response.choices[0].message.content
        except Exception as e:
            default_logger.error(f"LLM 调用失败: {e}")
            return f"生成失败:{str(e)}"


# 全局实例
llm_client = LLMClient()