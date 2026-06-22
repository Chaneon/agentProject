from typing import Dict, Tuple, List, Any

from pip._internal.resolution.resolvelib import candidates
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.services.llm_factory import LLMFactory
from app.tools.reranker import Reranker
from app.tools.retriever import KnowledgeRetriever

"""
知识库问答 Agent：
- 双路召回（向量 + BM25）获取候选文档
- 使用小模型（Cross-Encoder）重排序，取最相关的 top_k
- 将检索到的文档作为上下文，调用 LLM 生成答案
"""
class KnowledgeAgent:
    def __init__(self, user_info: Dict):
        self.user_info = user_info
        self.llm = LLMFactory
        # 初始化向量化模型
        embed_model =SentenceTransformer(settings.EMBEDDING_MODEL)
        self.retriever = KnowledgeRetriever(embed_model=embed_model, collection_name=settings.MILVUS_KNOWLEGE_COLLECTION)
        # 初始化检索器（使用知识库集合）
        self.reranker = Reranker(model_name=settings.RERANK_MODEL)

    def answer_question(self, question: str) -> Tuple[str, List[str]]:
        """
        回答问题的主流程：
        1. 双路召回获得候选文档（例如 10 个）
        2. 重排模型精排，取前 3 个
        3. 拼接上下文，调用 LLM 生成答案
        """
        # 1. 双路召回（向量 + BM25 融合），取前 10 个候选
        candidates = self.retriever.hybrid_retrive(question, top_k=10, alpha=0.7)
        if not candidates:
            return "未找到相关知识。",[]
        # 2. 重排模型精排，取前 3 个
        reranked = self.reranker.rerank(question,candidates, top_k=3)
        # 提取上下文文本和来源
        contexts = [doc['text'] for doc in reranked]
        sources = list(set([doc.get("doc_id", "unknown") for doc in reranked]))
        # 3. 构建 LLM 提示词
        prompt = f"""你是一个银行经营分析助手。请根据以下参考知识回答用户问题。
                如果无法从参考知识中找到答案，请如实告知，不要编造信息。
                参考知识：
                {chr(10).join(contexts)}
                用户问题：{question}
                回答：
                """
        answer = self.llm.complete(prompt, max_tokens=500)
        return  answer, sources

    async def process(self, message: str) -> Dict[str, Any]:
        """异步处理入口，与 Agent 接口保持一致"""
        answer, sources = self.answer_question(message)
        return {"reply": answer, "extra": {"sources": sources}}