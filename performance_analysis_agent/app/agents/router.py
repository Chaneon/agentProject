from email.mime import message
from typing import Dict
from unittest import result

from langgraph.constants import END
from langgraph.graph import StateGraph

from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.qa_agent import QAAgent
from app.agents.report_agent import ReportAgent
from app.agents.simulation_agent import SimulationAgent
from app.agents.state import GraphState, AgentType

"""
路由Agent：
- 使用规则+LLM 对用户消息进行意图分类
- 根据意图选择对应的专业 Agent
- 构建 LangGraph 工作流并执行
"""
class AgentRouter:
    """路由管理器，负责构建和执行 LangGraph 流程"""
    def __init__(self):
        # 构建状态图
        self.graph = self.build_graph()

    def classify_intent(self, state: GraphState) -> GraphState:
        """
        意图分类节点：
        - 使用简单关键词规则快速识别
        - 必要时可调用 LLM 进行更细致的分类（此处简化）
        """
        message = state["message"].lower()
        # 规则匹配（优先级从高到低）
        if any(kw in message for kw in["测算", "假设", "影响","如果"]):
            intent = AgentType.SIMULATION
            confidence = 0.9
        elif any(kw in message for kw in["报告", "生成报告", "排行榜"]):
            intent = AgentType.REPORT
            confidence = 0.9
        elif any(kw in message for kw in["制度", "口径", "怎么计算","什么是"]):
            intent = AgentType.KNOWLEDGE
            confidence = 0.8
        else:
            # 默认归为问答
            intent = AgentType.QA
            confidence = 0.7

        state["intent"] = intent
        state["confidence"] = confidence
        return state

    def route_by_intent(self, state: GraphState)->AgentType:
        """返回下一个节点名称"""
        return state["intent"]

    async def run_qa(self, state: GraphState) ->GraphState:
        """执行智能问答 Agent"""
        qa_agent = QAAgent(state["user_info"])
        result = await qa_agent.process(state["message"], state["user_info"])
        state["final_reply"] = result["reply"]
        state["final_extra"] = result.get("extra","")
        state["final_output"] = result
        return state

    async def run_simulation(self, state: GraphState) ->GraphState:
        """执行模拟测算 Agent（需要动态传入 user_info）"""
        sim_agent = SimulationAgent(state["user_info"])
        result = await sim_agent.process(state["message"], state["user_info"])
        state["final_reply"] = result["reply"]
        state["final_extra"] = result.get("extra","")
        state["final_output"] = result
        return state

    async def run_report(self, state: GraphState) ->GraphState:
        """执行报告生成 Agent"""
        report_agent = ReportAgent(state["user_info"])
        result = await report_agent.process(state["message"], state["user_info"])
        state["final_reply"] = result["reply"]
        state["final_extra"] = result.get("extra","")
        state["final_output"] = result
        return state

    async def run_knowledge(self, state: GraphState) ->GraphState:
        """执行知识库问答 Agent"""
        knowledge_agent = KnowledgeAgent(state["user_info"])
        result = await knowledge_agent.process(state["message"], state["user_info"])
        state["final_reply"] = result["reply"]
        state["final_extra"] = result.get("extra","")
        state["final_output"] = result
        return state

    def build_graph(self):
        """构建 LangGraph 工作流"""
        workflow = StateGraph(GraphState)
        # 添加节点
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("qa", self.run_qa)
        workflow.add_node("simulation", self.run_simulation)
        workflow.add_node("report", self.run_report)
        workflow.add_node("knowledge", self.run_knowledge)
        # 设置入口
        workflow.set_entry_point("classify_intent")
        # 条件边：根据意图类型跳转到对应节点
        workflow.add_conditional_edges(
            "classify_intent",
            self.route_by_intent(),
            {
                AgentType.QA: "qa",
                AgentType.SIMULATION: "simulation",
                AgentType.REPORT: "report",
                AgentType.KNOWLEDGE: "knowledge"
            }
        )
        # 所有 Agent 节点执行完毕后直接结束
        workflow.add_node("qa", END)
        workflow.add_node("simulation", END)
        workflow.add_node("report", END)
        workflow.add_node("knowledge", END)

        return workflow.compile()

    async def route(self, message: str, user_info: Dict, session_id: str)->Dict:
        """
       外部调用入口：
       - 初始化状态
       - 执行工作流
       - 返回最终回复和附加信息
       """
        initial_state: GraphState = {
            "message": message,
            "user_info": user_info,
            "session_id": session_id,
            "intent": None,
            "confidence": None,
            "agent_output": None,
            "final_reply": None,
            "final_extra": None,
            "error": None,
        }
        final_state = await self.graph.ainvoke(initial_state)
        return {
            "agent_type":final_state["intent"].value if final_state["intent"] else None,
            "reply": final_state["final_reply"],
            "extra": final_state["final_extra"]
        }
