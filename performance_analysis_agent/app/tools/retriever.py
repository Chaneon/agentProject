from typing import List, Dict

import jieba
import numpy as np
from rank_bm25 import BM25Okapi

from app.core.db import get_milvus_knowledge_collection, get_milvus_procedure_collection

"""
双路召回检索器：
- 向量检索（语义相似度）
- BM25 关键词检索（精确匹配）
- 分数融合（加权求和）
所有向量均经过 L2 归一化，Milvus 使用内积距离。
"""

class KnowledgeRetriever:
    def __init__(self, embed_mode:str, collection_name: str="knowledge_base"):
        """
        :param embed_model: SentenceTransformer 模型实例
        :param collection_name: Milvus 集合名称
        """
        # 根据集合名称选择对应的 Milvus 集合
        if collection_name == "knowledge_base":
            self.collection = get_milvus_knowledge_collection()
        else:
            self.collection = get_milvus_procedure_collection()
        self.embed_model = embed_mode
        self.collection.load()  # 加载到内存

    @staticmethod
    def l2_normalize(vec: List[float])->List[float]:
        """L2 归一化，使向量模长为1（用于查询和插入前的向量）"""
        arr = np.array(vec)
        norm = np.linalg.norm(arr)
        if norm == 0:
            return vec
        return (arr/norm).tolist()

    def chinese_tokenizer(self, text:str)-> List[str]:
        """中文分词器，用于 BM25"""
        return list(jieba.cut(text))

    def vector_search(self, query:str, top_k: int=20)->List[Dict]:
        """
        向量检索：将查询向量化，在 Milvus 中搜索最相似的文档
        """
        # 生成查询向量并归一化
        query_vec = self.embed_model.encode(query).tolist()
        query_vec = self.l2_normalize(query_vec)
        # Milvus 搜索参数（使用内积，因为向量已归一化）. nprobe 用于平衡检索的准确性和性能，1-100，越小，检索速度快，召回率低，默认是10
        search_params = {"metric_type":"IP", "params":{"nprobe": 10}}
        results = self.collection.search(
            data = [query_vec],
            anns_field= "embedding",
            param=search_params,
            limit=top_k,
            output_fields=["doc_id", "text", "metadata"]
        )
        docs=[]
        for hits in results:
            for hit in hits:
                docs.append({
                    "doc_id": hit.entity.get("doc_id"),
                    "text": hit.entity.get("text"),
                    "metadata": hit.entity.get("metadata"),
                    "vectore_score": hit.score      # 内积值，范围 [-1,1]
                })
        return  docs

    def bm25_search(self,query:str, candidates:List[Dict])->List[Dict]:
        """
        对候选文档列表计算 BM25 分数（基于文本内容）
        :param candidates: 向量检索返回的候选列表
        :return: 添加了 bm25_score 字段的列表，并按分数降序排序
        """
        if not candidates:
            return []

        texts = [doc['text'] for doc in candidates]
        # 对文档集合进行分词
        tokenized_corpus = [self.chinese_tokenizer(t) for t in texts]
        bm25 =BM25Okapi(tokenized_corpus)
        # 对查询分词
        tokenized_query = self.chinese_tokenizer(query)
        scores = bm25.get_scores(tokenized_query)
        for i, doc in enumerate(candidates):
            doc['bm25_score'] = float(scores[i])
        # 按 BM25 分数降序排序
        return sorted(candidates, key=lambda x: x['bm25_score'], reverse=True)

    def fuse_scores(self,vector_results: List[Dict], bm25_results: List[Dict], alpha:float = 0.7)->List[Dict]:
        """
        融合向量分数和 BM25 分数（加权归一化）
        :param alpha: 向量分数的权重，BM25 权重为 1-alpha，大部分向量的占比回避关键字高，7:3是目前市场比较多的情况，也可自定义
        :return: 融合后按 fusion_score 降序的文档列表
        """
        if not vector_results:
            return []
        doc_map = {}
        # 先处理向量结果
        for doc in vector_results:
            doc_id = doc['doc_id']
            doc_map[doc_id] = doc
            # 向量分数到 [0,1]（避免负值）
            norm_vec_score = max(0.0, doc['vectore_score'])
            doc_map[doc_id]['fuse_score'] = alpha * norm_vec_score

        # 处理 BM25 结果
        if bm25_results:
            bm25_alpha = 1-alpha
            # 找到 BM25 分数的最大值用于归一化。因为关键字的评分是1-100，选他最大值，然后除最大值，那么除了最大值为1，其他值都小于1
            max_bm25 = max((d.get('bm25_score', 0) for d in bm25_results), default= 1.0)
            if max_bm25 == 0:
                max_bm25 = 1
            for doc in bm25_results:
                doc_id = doc['doc_id']
                norm_bm25_score = doc.get('bm25_score', 0)/max_bm25
                if doc_id in doc_map:
                    doc_map[doc_id]['fuse_score'] += bm25_alpha * norm_bm25_score
                else:
                    # 理论上 BM25 结果应该是向量结果子集，但做兼容处理
                    new_doc = doc.copy()
                    new_doc['fuse_score'] = bm25_alpha * norm_bm25_score
                    new_doc['vectore_score'] = 0
                    doc_map[doc_id]=new_doc
            # 按融合分数降序排序
            return sorted(doc_map.values(), key=lambda x: x['fuse_score'], reverse=True)

    def hybrid_retrive(self, query:str, top_k: int=10,  alpha:float = 0.7):
        """
           完整的双路召回流程：
           1. 向量检索（取 top 20）
           2. BM25 对候选打分
           3. 分数融合
           4. 返回 top_k 个文档
       """
        # 向量检索，取较多候选（20个）
        vector_candidates = self.vector_search(query, top_k=20)
        if not vector_candidates:
            return []
        # BM25 打分
        bm25_ranked = self.bm25_search(query,vector_candidates)
        # 融合
        fused = self.fuse_scores(vector_candidates, bm25_ranked, alpha)
        return fused[:top_k]


