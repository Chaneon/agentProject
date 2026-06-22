from typing import Dict

from app.core.llm_client import llm_client
from app.core.config import settings
from app.utils.logger import log

"""
回答生成节点 - 综合所有信息生成回复
"""
async def generation_node(state: Dict) -> Dict:
    """回答生成节点"""
    message = state.get("message", "")
    intent = state.get("intent", "")
    emotion = state.get("emotion", "")
    products = state.get("retrieved_products", [])
    faqs = state.get("retrieved_faqs", [])
    memories = state.get("retrieved_memories", [])
    history = state.get("short_term_memory", [])
    work_memory = state.get("work_memory", {})
    user_info = state.get("user_info", {})

    log.info(f"生成回复: intent={intent}, emotion={emotion}")

    # 检查转人工
    if intent == "transfer" or emotion == "angry":
        state["need_transfer"] = True
        state["transfer_reason"] = "用户要求转人工" if intent == "transfer" else "用户情绪愤怒"
        state["reply"] = "很抱歉给您带来不便，我帮您转接人工客服，请稍等..."
        return state

    # 构建 Prompt
    product_text = "\n".join([f"- {p['name']}: {p.get('selling_points', '')}" for p in products[:3]])
    faq_text = "\n".join([f"Q: {f['question']}\nA: {f['answer'][:200]}" for f in faqs[:2]])
    memory_text = "\n".join(memories[:2])
    history_text = "\n".join([f"{h['role']}: {h['content']}" for h in history[-6:]])

    prompt = f"""你是电商客服助手，请回复用户问题。

用户：{user_info.get('real_name', '用户')}
{product_text}
{faq_text}
{memory_text}
{history_text}

用户问题：{message}

请简洁回复（不超过150字）："""
    reply = await llm_client.chat(prompt, max_tokens=300, temperature=settings.LLM_TEMPERATURE)

    # 处理工作记忆（退换货流程）
    work_update = None
    if intent == "after_sale" and "退换货" in message and work_memory.get("state") == "idle":
        work_update = {"state": "waiting_order_no", "data": {"action": "return_exchange"}}
        reply += " 请提供您的订单号，以便为您处理退换货。"

    state["reply"] = reply.strip()
    state["work_memory_update"] = work_update
    return state