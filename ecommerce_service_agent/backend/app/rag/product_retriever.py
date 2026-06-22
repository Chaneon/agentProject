from typing import List, Dict

from app.core.embedding import embedding_model
from app.core.milvus_client import milvus_client
from app.core.config import settings
from app.utils.logger import log

"""
商品RAG检索器 - 从向量库检索相关商品
"""
class ProductRetriever:
    def __init__(self):
        self.collection_name = settings.MILVUS_PRODUCT_COLLECTION

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        try:
            vector = embedding_model.encode(query)
            results = milvus_client.search(self.collection_name, vector, top_k)
            products = []
            for r in results:
                meta = r.get("metadata", {})
                products.append({
                    "product_id": meta.get("product_id"),
                    "name": meta.get("name"),
                    "price": meta.get("price"),
                    "score": r["score"]
                })
            return products
        except Exception as e:
            log.error(f"商品检索失败: {e}")
            return []


product_retriever = ProductRetriever()