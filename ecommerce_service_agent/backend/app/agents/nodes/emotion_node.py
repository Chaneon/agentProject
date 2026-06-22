import json
import re
from typing import Dict

from app.core.llm_client import llm_client
from app.utils.logger import log

"""
情绪识别节点 - 识别用户情绪
"""
async def emotion_node(state: Dict) -> Dict:
    """情绪识别节点"""
    message = state.get("message", "")
    log.info(f"情绪识别: {message[:50]}...")

    msg_lower = message.lower()

    # 快速规则
    if any(kw in msg_lower for kw in ["差评", "投诉", "垃圾", "生气", "愤怒"]):
        state["emotion"] = "angry"
        return state
    if any(kw in msg_lower for kw in ["谢谢", "感谢", "很好", "满意"]):
        state["emotion"] = "positive"
        return state
    if any(kw in msg_lower for kw in ["不好", "不行", "差", "慢"]):
        state["emotion"] = "negative"
        return state

    # LLM分类
    prompt = f"""判断情绪，只输出JSON：{{"emotion": "positive/neutral/negative/angry"}}
用户消息：{message}"""
    try:
        response = await llm_client.chat(prompt, max_tokens=100)
        match = re.search(r'\{.*\}', response)
        if match:
            result = json.loads(match.group())
            state["emotion"] = result.get("emotion", "neutral")
        else:
            state["emotion"] = "neutral"
    except Exception:
        state["emotion"] = "neutral"

    return state