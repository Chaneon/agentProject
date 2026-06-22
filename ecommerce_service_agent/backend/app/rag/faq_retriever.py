from typing import List, Dict

from app.core.embedding import embedding_model
from app.core.milvus_client import milvus_client
from app.core.config import settings
from app.utils.logger import log

"""
FAQ-RAG检索器 - 从向量库检索相关FAQ
"""
class FaqRetriever:
    def __init__(self):
        self.collection_name = settings.MILVUS_FAQ_COLLECTION
        self.threshold = 0.7

    async def search(self, query: str, top_k: int = 3) -> List[Dict]:
        try:
            vector = embedding_model.encode(query)
            results = milvus_client.search(self.collection_name, vector, top_k)
            faqs = []
            for r in results:
                if r["score"] < self.threshold:
                    continue
                meta = r.get("metadata", {})
                faqs.append({
                    "faq_id": meta.get("faq_id"),
                    "question": meta.get("question"),
                    "answer": r["text"][:500],
                    "score": r["score"]
                })
            return faqs
        except Exception as e:
            log.error(f"FAQ检索失败: {e}")
            return []


faq_retriever = FaqRetriever()