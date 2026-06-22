import json
import re
from typing import Dict, List, Any
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.db import get_mysql_session
from app.services.llm_factory import LLMFactory
from app.tools.retriever import KnowledgeRetriever
from app.tools.stored_procedure_executor import StoredProcedureExecutor

"""
模拟测算 Agent：
- 通过 RAG 检索最匹配的存储过程定义
- 使用 LLM 从用户消息中提取参数
- 调用存储过程执行测算
- 返回自然语言结果
"""
class SimulationAgent:
    def __init__(self, user_info: Dict):
        self.user_info = user_info
        self.llm = LLMFactory()
        self.db_session = get_mysql_session()
        # 存储过程执行器
        self.proc_executor = StoredProcedureExecutor()
        # 用户所属机构ID
        self.org_id = user_info.get("org_id")
        # 初始化检索器（专门用于存储过程定义集合）
        embed_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.retriever = KnowledgeRetriever(embed_model, collection_name=settings.MILVUS_PROCEDURE_COLLECTION)

    def retrieve_procedure(self, query:str):
        """检索与用户查询最相关的存储过程定义"""
        # 双路召回 + 融合，取最相关的一个
        candidates = self.retriever.hybrid_retrive(query, top_k=1, alpha=0.7)
        if not candidates:
            return None
        best = candidates[0]
        return{
            "proc_name":best.get("metadata",{}).get("proc_name", best.get("doc_id")),
            "definition_text": best.get("text", ""),
            "score": best.get("fusion_score")
        }

    def extract_params_with_llm(self, user_query: str, proc_definition: str) ->List[Any]:
        """使用 LLM 从用户消息中提取存储过程所需的参数（按顺序）"""
        prompt = f"""
                    根据存储过程定义，从用户问题中提取参数值，按顺序输出JSON数组。
                    存储过程定义：
                    {proc_definition}
                    用户问题：{user_query}
                    当前用户机构ID：{self.org_id}（若参数需要机构ID，默认使用该值）
                    输出JSON数组，例如：[123, "2025-03-31", 10]
                    日期格式：YYYY-MM-DD。参数缺失时用 null。
                """
        response = self.llm.complete(prompt, max_tokens=200)
        # 使用正则提取 JSON 数组
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if not match:
            raise ValueError("未找到参数JSON数据")
        params = json.load(match.group())
        # 如果第一个参数是 null，自动填充机构ID
        if params and params[0] is None:
            params[0] = self.org_id
        return params

    def process(self, message: str) -> Dict[str, Any]:
        """处理模拟测算请求"""
        # 1. 检索存储过程
        proc_info = self.retrieve_procedure(message)
        if not proc_info:
            return {"reply":"未找到匹配的测算模型，请尝试更具体的描述", "extra":{"error":"no_procedure"}}
        proc_name = proc_info['proc_name']
        proc_definition = proc_info['definition_text']
        # 2. 提取参数
        try:
            params = self.extract_params_with_llm(message, proc_definition)
        except Exception as e:
            return {"reply":"无法提取所需参数，请提供完整信息（如日期、变动幅度等）。", "extra":{"error": str(e), "proc_name": proc_name}}
        # 3. 调用存储过程
        try:
            result = self.proc_executor.call_procedure(proc_name,params)
        except Exception as e:
            return {"reply":f"测算执行失败：{str(e)}", "extra":{"error": str(e), "proc_name": proc_name, "params": params}}
        # 4. 生成自然语言回复
        if result.get("rows") and len(result.get("rows")) > 0:
            impact_value = result['rows'][0][0] # 第一行第一列是结果
            reply_prompt = f"用户问题：{message}\n测算结果数值：{impact_value}\n请用一句话自然语言回复。"
            reply = self.llm.complete(reply_prompt, max_tokens=100)
            return  {"reply":reply.strip(), "extra":{"proc_name": proc_name, "params": params, "raw_result": result}}
        else:
            return  {"reply":"测算完成，但无返回数据", "extra":{"proc_name": proc_name, "params": params}}

    def close(self):
        self.proc_executor.close()


