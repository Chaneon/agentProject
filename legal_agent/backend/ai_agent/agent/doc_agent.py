from typing import Dict, Any

from core.llm_client import llm_client
from utils.logger import default_logger

"""
文书生成 Agent：根据事实和诉求生成法律文书
"""

class DocumentAgent:
    """文书生成 Agent"""

    async def generate(self, doc_type: str, facts: str, claims: str = None) -> Dict[str, Any]:
        """生成法律文书"""
        default_logger.info(f"生成文书: {doc_type}")

        # 构建 prompt
        prompt = f"""你是一位经验丰富的法律文书撰写专家。请根据以下信息，生成一份规范的{doc_type}。

案件事实：{facts}
诉讼请求：{claims if claims else '无'}

要求：
1. 格式规范，包含必要的标题、当事人信息、事实陈述、法律依据、请求事项等
2. 语言正式、严谨
3. 使用中国法律术语

请输出完整的{doc_type}内容（Markdown格式）：
"""
        content = llm_client.chat(prompt, max_tokens=3000)

        return {
            "doc_type": doc_type,
            "facts": facts,
            "claims": claims,
            "content": content
        }

doc_agent = DocumentAgent()