"""
Milvus 向量数据库初始化脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.milvus_client import milvus_client
from app.core.embedding import embedding_model
from app.utils.logger import log


async def init_collections():
    """初始化Milvus集合和示例数据"""
    log.info("开始初始化Milvus向量数据库...")

    # 示例商品数据
    sample_products = [
        {"doc_id": "product_1", "text": "户外三合一冲锋衣 防水透气 可拆卸内胆 防风保暖",
         "metadata": {"product_id": 1, "name": "户外三合一冲锋衣", "price": 39900}},
        {"doc_id": "product_2", "text": "运动蓝牙耳机 超长续航 Hi-Fi音质 IPX7防水",
         "metadata": {"product_id": 2, "name": "运动蓝牙耳机", "price": 12900}},
    ]

    for item in sample_products:
        vector = embedding_model.encode(item["text"])
        milvus_client.insert("product_vectors", item["doc_id"], item["text"], vector, item["metadata"])

    log.info("Milvus初始化完成")


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_collections())