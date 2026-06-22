
from typing import List

from app.core.embedding import embedding_model
from app.core.milvus_client import milvus_client
from app.core.config import settings
from app.utils.logger import log

"""
长期记忆RAG检索器 - 检索用户历史摘要
"""
class MemoryRetriever:
    def __init__(self):
        self.collection_name = settings.MILVUS_MEMORY_COLLECTION
        self.threshold = 0.6

    async def search(self, user_id: str, query: str, top_k: int = 3) -> List[str]:
        try:
            vector = embedding_model.encode(query)
            filter_expr = f'metadata["user_id"] == "{user_id}"'
            results = milvus_client.search(self.collection_name, vector, top_k, filter_expr)
            memories = [r["text"] for r in results if r["score"] >= self.threshold]
            return memories
        except Exception as e:
            log.error(f"记忆检索失败: {e}")
            return []


memory_retriever = MemoryRetriever()