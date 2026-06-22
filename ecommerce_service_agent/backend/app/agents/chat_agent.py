from typing import Dict, Any
from langgraph.graph import StateGraph, END

from app.agents.nodes.intent_node import intent_node
from app.agents.nodes.retrieval_node import retrieval_node
from app.agents.nodes.emotion_node import emotion_node
from app.agents.nodes.generation_node import generation_node
from app.services.memory_service import memory_service

"""
对话 Agent - 使用 LangGraph 编排对话处理流程

流程：
1. 意图识别 → 2. RAG检索 → 3. 情绪识别 → 4. 回答生成
"""
class ChatAgent:
    """对话 Agent 主编排器"""

    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self):
        """构建 LangGraph 工作流"""
        workflow = StateGraph(Dict)

        workflow.add_node("intent", intent_node)
        workflow.add_node("retrieval", retrieval_node)
        workflow.add_node("emotion", emotion_node)
        workflow.add_node("generation", generation_node)

        workflow.set_entry_point("intent")
        workflow.add_edge("intent", "retrieval")
        workflow.add_edge("retrieval", "emotion")
        workflow.add_edge("emotion", "generation")
        workflow.add_edge("generation", END)

        return workflow.compile()

    async def process(
            self,
            message: str,
            user_id: str,
            user_info: Dict,
            session_id: str,
            work_memory: Dict = None
    ) -> Dict[str, Any]:
        """处理用户消息"""
        short_term_memory = memory_service.get_short_term(session_id)

        initial_state = {
            "message": message,
            "user_id": user_id,
            "user_info": user_info,
            "session_id": session_id,
            "short_term_memory": short_term_memory,
            "work_memory": work_memory or {"state": "idle", "data": {}},
            "intent": None,
            "retrieved_products": [],
            "retrieved_faqs": [],
            "retrieved_memories": [],
            "emotion": None,
            "reply": "",
            "need_transfer": False,
            "transfer_reason": None,
            "work_memory_update": None
        }

        final_state = await self.graph.ainvoke(initial_state)

        return {
            "reply": final_state["reply"],
            "need_transfer": final_state.get("need_transfer", False),
            "transfer_reason": final_state.get("transfer_reason"),
            "intent": final_state.get("intent"),
            "emotion": final_state.get("emotion"),
            "work_memory_update": final_state.get("work_memory_update")
        }


chat_agent = ChatAgent()