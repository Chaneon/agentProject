from typing import List, Any, Dict

import numpy as np
from pymilvus import connections, FieldSchema, DataType, CollectionSchema, Collection
from pymilvus.orm import utility
from sentence_transformers import SentenceTransformer

from models.config import settings
from utils.logger import default_logger

"""
向量数据库操作模块：连接 Milvus，插入/检索向量
"""
# 全局变量
milvus_collecion = None
embedding_model = None
def init_milvus():
    """初始化 Milvus 连接和集合"""
    global  milvus_collecion, embedding_model

    # 连接 Milvus
    connections.connect(
        alias= "default",
        host= settings.milvus_host,
        port= settings.milvus_port
    )
    default_logger.info(f"已连接到 Milvus：{settings.milvus_host}:{settings.milvus_port}")
    # 加载 embedding 模型
    embedding_model:SentenceTransformer = SentenceTransformer(settings.embedding_model)
    default_logger.info(f"加载Embedding 模型：{settings.embedding_model}")

    # 创建集合（如果不存在）
    if not utility.has_collection(settings.milvus_collection):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, max_length=800),
            FieldSchema(name="metadata", dtype=DataType.JSON),
        ]
        schema = CollectionSchema(fields, description="法律知识库")
        milvus_collecion = Collection(settings.milvus_collection, schema)
        # 创建索引
        index_params = {
            "metric_type": "IP",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        milvus_collecion.create_index("embedding", index_params= index_params)
        default_logger.info(f"创建 Milvus 集合：{settings.milvus_collecion}")
    else:
        milvus_collecion = Collection(settings.milvus_collection)

    milvus_collecion.load()
    default_logger.info(" Milvus 加载完成！")

def get_collection()-> Collection:
    """获取 Milvus 集合实例"""
    if milvus_collecion is None:
        init_milvus()
    return milvus_collecion

def get_embedding_model():
    """获取 embedding 模型实例"""
    if embedding_model is None:
        init_milvus()
    return embedding_model

def l2_normalize(vec:List[float])->List[float]:
    """L2 归一化"""
    arr = np.array(vec) #转成numpy数组，方便计算
    norm = np.linalg.norm(arr) # 计算L2长度
    if norm == 0:
        return vec #防止除数为0
    return (arr/norm).tolist() # arr的每个元素除以长度，组成新的集合

def insert_doc(docs: List[Dict[str, Any]]):
    """插入文档到 Milvus（需先向量化）"""
    collection = get_collection()
    model = get_embedding_model()

    doc_ids = []
    texts = []
    embeddings = []
    metadatas = []

    for doc in docs:
        doc_id = doc.get("doc_id")
        text = doc.get("text")
        metadata = doc.get("metadata")
        # 生成向量并归一化
        vec = model.encode(text).toList()
        embedding = l2_normalize(vec)

        doc_ids.append(doc_id)
        texts.append(text)
        embeddings.append(embedding)
        metadatas.append(metadata)

    collection.insert(doc_ids, texts, embeddings, metadatas)
    collection.flush()
    default_logger.info(f"已插入{len(docs)}个文档到Milvus")

def search_similar(query:str, top_k:int = 5)->List[Dict[str, Any]]:
    """搜索相似文档"""
    collection = get_collection()
    model = get_embedding_model()

    # 向量化查询并归一化
    query_vec = model.encode(query).toList()
    query_embedding = l2_normalize(query_vec)

    search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
    result = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param= search_params,
        limit = top_k,
        output_fields= ["doc_id", "text", "metadata"]
    )

    docs=[]
    if result:
        for res in result:
            for doc in res:
                doc_id = doc.entity.get("doc_id")
                text = doc.entity.get("text")
                metadata = doc.entity.get("metadata")
                docs.append({
                    "doc_id" : doc_id,
                    "text" : text,
                    "metadata" : metadata
                })
    return docs