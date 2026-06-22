import json
import re
from typing import Dict

from app.core.llm_client import llm_client
from app.utils.logger import log

"""
意图识别节点 - 判断用户意图
"""
async def intent_node(state: Dict) -> Dict:
    """意图识别节点"""
    message = state.get("message", "")
    log.info(f"意图识别: {message[:50]}...")

    # 快速规则匹配
    msg_lower = message.lower()

    # 转人工关键词
    if any(kw in msg_lower for kw in ["人工客服", "转人工", "找真人"]):
        state["intent"] = "transfer"
        state["intent_confidence"] = 0.95
        return state

    # 售后关键词
    if any(kw in msg_lower for kw in ["退货", "换货", "退款", "物流", "快递"]):
        state["intent"] = "after_sale"
        state["intent_confidence"] = 0.85
        return state

    # 售前关键词
    if any(kw in msg_lower for kw in ["多少钱", "价格", "推荐", "参数", "规格", "库存"]):
        state["intent"] = "pre_sale"
        state["intent_confidence"] = 0.85
        return state

    # LLM分类（兜底）
    prompt = f"""判断意图，只输出JSON：{{"intent": "pre_sale/after_sale/chitchat/transfer"}}
用户消息：{message}"""
    try:
        response = await llm_client.chat(prompt, max_tokens=100)
        match = re.search(r'\{.*\}', response)
        if match:
            result = json.loads(match.group())
            state["intent"] = result.get("intent", "chitchat")
        else:
            state["intent"] = "chitchat"
    except Exception:
        state["intent"] = "chitchat"

    return state