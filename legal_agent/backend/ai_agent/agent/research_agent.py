from typing import Dict, Any

from core.llm_client import llm_client
from core.vector_store import search_similar
from utils.logger import default_logger

"""
法律研究 Agent：检索法规案例 + 生成分析报告
"""
class ResearchAgent:
    def research(self, query:str)-> Dict[str, Any]:
        """执行法律研究：检索 + 生成分析报告"""
        default_logger.info(f"开始法律研究：{query}")
        # 1. 检索相关法规和案例
        retrieved = search_similar(query, top_k=5)
        laws = []
        cases = []

        for doc in retrieved:
            metadata = doc.get("metadata",{})
            doc_type = metadata.get("type", "unknown")
            title = metadata.get("title", "")
            text = metadata["text"][:500]
            if doc_type == "law":
                laws.append({"title": title, "content": text})
            elif doc_type == "case":
                cases.append({"title": title, "summary": text})
            else:
                # 默认当作法规
                laws.append({"title": doc["doc_id"], "content": text})

            report_prompt =  f"""用户问题：{query}
            检索到的法规：
            {chr(10).join([f"- {l['title']}: {l['content']}" for l in laws[:3]])}
            检索到的案例：
            {chr(10).join([f"- {c['title']}: {c['summary']}" for c in cases[:3]])}
            请根据以上信息，生成一份类案分析报告，包括：
            1. 相关法规要点
            2. 类似案例裁判要旨
            3. 对用户问题的法律分析结论
            """
            report = llm_client.chat(report_prompt, max_tokens=2000)

        return {
            "query": query,
            "laws": laws,
            "cases": cases,
            "report": report
        }

research_agent = ResearchAgent()