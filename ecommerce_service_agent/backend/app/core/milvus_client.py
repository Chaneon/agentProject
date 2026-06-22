from typing import List, Dict
from pymilvus import connections, Collection, utility, FieldSchema, CollectionSchema, DataType
import numpy as np

from app.core.config import settings
from app.utils.logger import log

"""
Milvus 向量数据库客户端

功能：
1. 连接 Milvus
2. 管理商品、FAQ、历史摘要向量集合
3. 向量插入和检索
"""
class MilvusClient:
    """Milvus 客户端封装（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        connections.connect(alias="default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
        log.info(f"Milvus 连接成功: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")

        # 初始化三个集合
        self.product_collection = self._get_or_create_collection(settings.MILVUS_PRODUCT_COLLECTION)
        self.faq_collection = self._get_or_create_collection(settings.MILVUS_FAQ_COLLECTION)
        self.memory_collection = self._get_or_create_collection(settings.MILVUS_MEMORY_COLLECTION)

    def _get_or_create_collection(self, collection_name: str) -> Collection:
        """获取或创建集合"""
        if utility.has_collection(collection_name):
            collection = Collection(collection_name)
            collection.load()
            log.info(f"加载已有集合: {collection_name}")
        else:
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=128),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
                FieldSchema(name="metadata", dtype=DataType.JSON)
            ]
            schema = CollectionSchema(fields, description=f"{collection_name} 向量集合")
            collection = Collection(collection_name, schema)
            index_params = {"metric_type": "IP", "index_type": "IVF_FLAT", "params": {"nlist": 128}}
            collection.create_index("embedding", index_params)
            log.info(f"创建新集合: {collection_name}")
        return collection

    @staticmethod
    def _l2_normalize(vector: List[float]) -> List[float]:
        """L2 归一化"""
        arr = np.array(vector)
        norm = np.linalg.norm(arr)
        return (arr / norm).tolist() if norm != 0 else vector

    def search(self, collection_name: str, query_vector: List[float],
               top_k: int = 5, filter_expr: str = None) -> List[Dict]:
        """向量检索"""
        collection = self._get_or_create_collection(collection_name)
        query_vector = self._l2_normalize(query_vector)
        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=["doc_id", "text", "metadata"]
        )

        docs = []
        for hits in results:
            for hit in hits:
                docs.append({
                    "doc_id": hit.entity.get("doc_id"),
                    "text": hit.entity.get("text"),
                    "metadata": hit.entity.get("metadata"),
                    "score": hit.score
                })
        return docs

    def insert(self, collection_name: str, doc_id: str, text: str,
               embedding: List[float], metadata: dict = None):
        """插入向量数据"""
        collection = self._get_or_create_collection(collection_name)
        embedding = self._l2_normalize(embedding)
        collection.insert([[doc_id], [text], [embedding], [metadata or {}]])
        collection.flush()

    def insert_batch(self, collection_name: str, items: List[Dict]):
        """批量插入"""
        collection = self._get_or_create_collection(collection_name)
        doc_ids = [item["doc_id"] for item in items]
        texts = [item["text"] for item in items]
        embeddings = [self._l2_normalize(item["embedding"]) for item in items]
        metadatas = [item.get("metadata", {}) for item in items]
        collection.insert([doc_ids, texts, embeddings, metadatas])
        collection.flush()

    def delete_by_filter(self, collection_name: str, filter_expr: str):
        """按条件删除"""
        collection = self._get_or_create_collection(collection_name)
        collection.delete(filter_expr)
        collection.flush()


milvus_client = MilvusClient()