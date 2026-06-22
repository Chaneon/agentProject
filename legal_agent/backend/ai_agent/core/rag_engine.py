from core.llm_client import llm_client
from core.vector_store import search_similar

"""
RAG 检索增强生成引擎：结合向量检索和 LLM 生成答案
"""
class RAGEngine:
    @staticmethod
    def retrive_context(query:str, top_k:int = 3)->str:
        """检索相关上下文，拼接为文本"""
        docs = search_similar(query, top_k=top_k)
        if not docs:
            return ""
        context_parts = []
        for i, doc in enumerate(docs):
            context_parts.append(f"【参考文档{i+1}】\n{doc['text']}\n")
        return "\n".join(context_parts)

    @staticmethod
    def  generate_with_context(query:str, system_prompt:str=None)->str:
        """使用 RAG 检索上下文，生成回答"""
        context = RAGEngine.retrive_context(query)
        # 无检索结果，直接使用 LLM
        if not context:
            return llm_client.chat(query)
        # 构建 prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n参考信息：\n{context}\n\n用户问题：{query}\n回答："
        else:
            full_prompt = f"参考以下信息回答：\n\n{context}\n\n用户问题：{query}\n回答："
        return llm_client.chat(full_prompt)

rag_engine = RAGEngine()