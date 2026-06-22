import asyncio
from typing import Dict

from app.rag.product_retriever import product_retriever
from app.rag.faq_retriever import faq_retriever
from app.rag.memory_retriever import memory_retriever
from app.utils.logger import log

"""
RAG检索节点 - 并行检索商品、FAQ、历史记忆
"""
async def retrieval_node(state: Dict) -> Dict:
    """RAG检索节点"""
    message = state.get("message", "")
    user_id = state.get("user_id", "")
    intent = state.get("intent", "")
    log.info(f"RAG检索: intent={intent}")

    # 根据意图决定检索类型
    need_product = intent == "pre_sale"
    need_faq = intent in ["pre_sale", "after_sale"]
    need_memory = True

    tasks = []
    tasks.append(product_retriever.search(message, top_k=5) if need_product else asyncio.sleep(0, result=[]))
    tasks.append(faq_retriever.search(message, top_k=3) if need_faq else asyncio.sleep(0, result=[]))
    tasks.append(memory_retriever.search(user_id, message, top_k=3) if need_memory else asyncio.sleep(0, result=[]))

    results = await asyncio.gather(*tasks)
    state["retrieved_products"] = results[0]
    state["retrieved_faqs"] = results[1]
    state["retrieved_memories"] = results[2]

    log.info(f"检索完成: 商品={len(state['retrieved_products'])}, FAQ={len(state['retrieved_faqs'])}, 记忆={len(state['retrieved_memories'])}")
    return state