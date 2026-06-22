from enum import Enum
from typing import TypedDict, Dict, Optional, Any

"""
定义 LangGraph 工作流中各个节点共享的状态对象。
使用 TypedDict 提供类型提示。
"""
class AgentType(str, Enum):
    """支持的 Agent 类型枚举"""
    QA = "qa"                       # 智能问答
    SIMULATION = "simulation"       # 模拟测算
    REPORT = "report"               # 报告生成
    KNOWLEDGE = "knowledge"         # 知识库问答

class GraphState(TypedDict):
    """
   LangGraph 状态对象。
   各个节点可以读取和修改这些字段。
   """
    message: str                                # 用户原始消息
    user_info: Dict[str, Any]                   # 用户信息（user_id, role, org_id等）
    session_id: str                             # 会话ID
    intent: Optional[AgentType]                 # 识别出的意图类型
    confidence: Optional[float]            # 意图分类置信度
    agent_output: Optional[Dict[str, Any]]      # Agent 执行后的详细输出
    final_reply: Optional[str]                  # 最终给用户的回复文本
    final_extra: Optional[Dict]                 # 附加信息（如 SQL、测算参数等）
    error: Optional[str]                        # 错误信息