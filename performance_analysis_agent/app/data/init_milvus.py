import sys
import os

from fastapi import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import init_milvus, get_milvus_knowledge_collection, get_milvus_procedure_collection
from sentence_transformers import SentenceTransformer
from app.core.config import settings
import glob
import numpy as np

"""
初始化 Milvus 集合：知识库和存储过程库
所有向量在插入前进行 L2 归一化
"""
def l2_normalize(vec):
    """L2 归一化"""
    arr = np.array(vec)
    norm = np.linalg.norm(arr)
    if norm == 0:
        return vec
    return (arr / norm).tolist()

def init_knowledge_base():
    """初始化知识库集合：插入示例文档"""
    collection = get_milvus_knowledge_collection()
    model = SentenceTransformer(settings.EMBEDDING_MODEL)

    # 示例文档（实际应从外部文件读取）
    docs = [
        {
            "doc_id": "doc_001",
            "text": "绩效考核管理办法：员工绩效分为A、B、C、D四档，连续两次D将进行培训。",
            "metadata": {"category": "制度"}
        },
        {
            "doc_id": "doc_002",
            "text": "FTP利润指标口径：FTP利润 = 业务收入 - FTP成本，其中FTP成本根据期限匹配。",
            "metadata": {"category": "指标口径"}
        }
    ]

    # 以下代码是从外部文件读取，为了获取category，这边把category当做文件名前缀
    # docs = []
    # know_path = "data/internal_knowledge"
    # if not os.path.exists(know_path):
    #     os.makedirs(know_path)
    #     print(f"请将公司内部知识库定义文档放入 {know_path} 目录")
    #     return
    #
    # # glob：用通配符查找文件和文件夹，返回的是个列表
    # for file_path in glob.glob(f"{know_path}/*.txt"):
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         text = f.read()
    #         filename  = Path(file_path).stem  # 文件名（不含扩展名）
    #
    #         # 支持多种分隔符
    #         separators = ["_", "-", "：",":"]
    #         category = "未分类"
    #
    #         for sep in separators:
    #             if sep in filename:
    #                 parts = filename.split(sep, 1)
    #                 category = parts[0]
    #                 doc_id = parts[1]
    #                 break
    #
    #         docs.append({
    #             "doc_id": doc_id,
    #             "text": text,
    #             "metadata": { "category": category , "source": file_path, "file_type": "md"}
    #         })

    for doc in docs:
        embedding = model.encode(doc["text"]).tolist()
        embedding = l2_normalize(embedding)
        collection.insert([doc["doc_id"], doc["text"], embedding, doc["metadata"]])






    collection.flush()
    print("知识库初始化完成（向量已归一化）")

def init_procedure_base():
    """初始化存储过程集合：从 data/stored_procedures/ 目录读取 Markdown 文件"""
    collection = get_milvus_procedure_collection()
    model = SentenceTransformer(settings.EMBEDDING_MODEL)

    proc_dir = "data/stored_procedures"
    if not os.path.exists(proc_dir):
        os.makedirs(proc_dir)
        print(f"请将存储过程定义文档放入 {proc_dir} 目录")
        return

    # glob：用通配符查找文件和文件夹，返回的是个列表
    for file_path in glob.glob(f"{proc_dir}/*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        proc_name = os.path.basename(file_path).replace(".txt", "")
        embedding = model.encode(text).tolist()
        embedding = l2_normalize(embedding)
        collection.insert([proc_name, text, embedding, {"proc_name": proc_name}])
    collection.flush()
    print("存储过程知识库初始化完成（向量已归一化）")

if __name__ == "__main__":
    init_milvus()
    init_knowledge_base()
    init_procedure_base()