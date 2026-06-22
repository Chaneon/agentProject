import json
from typing import TypedDict, List, Any, Dict

from langgraph.constants import END
from langgraph.graph import StateGraph

from core.document_parser import DocumentParser
from core.llm_client import llm_client

"""
合同审查 Agent：使用 LangGraph 实现多步骤合同审查流程
"""
class ContractState(TypedDict):
    """合同审查状态"""
    file_bytes: bytes
    filename: str
    raw_text: str
    chunks: List[str]
    risk_analysis: str
    risk_level: str
    suggestions: List[str]
    report: str

class ContractAgent:

    def __init__(self):
        self.graph = self.build_graph()

    def parse_document(self, state:ContractState) -> ContractState:
        """解析文档：提取文本并分块"""
        raw_text, chunks = DocumentParser.parse_and_split(state.get("file_bytes"), state.get("filename"))
        state["raw_text"] = raw_text
        state["chunks"] = chunks
        return state

    def analyze_risk(self,state:ContractState) -> ContractState:
        """风险分析：使用 LLM 识别风险条款"""
        # 取前 3 个块（合同通常开头部分包含关键条款）
        preview = "\n".join(state["chunks"][:3])
        prompt = f"""你是一位专业的合同审查律师。请分析以下合同内容，识别潜在风险条款，并给出风险等级（高/中/低）和改进建议。
        合同内容：
        {preview[:3000]}
        
        请以 JSON 格式输出：
        {{"risk_level": "high/middle/low", "analysis": "风险分析描述", "suggestions": ["建议1", "建议2"]}}
        """
        response = llm_client.chat(prompt, max_tokens=1000)

        try:
            result = json.loads(response)
            state['risk_level'] = result.get("risk_level", "middle")
            state['risk_analysis'] = result.get("analysis", "")
            state['suggestions'] = result.get("suggestions", [])
        except:
            state['risk_level'] = "middle"
            state['risk_analysis'] = response
            state['suggestions'] = []
        return state

    def generate_report(self, state: ContractState) -> ContractState:
        """生成审查报告"""
        report_prompt = f"""请根据以下信息生成一份完整的合同审查报告：
            合同名称：{state['filename']}
            风险等级：{state['risk_level']}
            风险分析：{state['risk_analysis']}
            改进建议：{', '.join(state['suggestions']) if state['suggestions'] else '无'}
            
            请生成格式规范、内容清晰的报告（Markdown格式）。
            """
        state['report'] = llm_client.chat(report_prompt, max_tokens=1500)
        return state

    async def review(self, file_bytes: bytes, filename:str)-> Dict[str, Any]:
        """执行合同审查"""
        initial_state = {
            "file_bytes": file_bytes,
            "filename": filename,
            "raw_text": "",
            "chunks": [],
            "risk_analysis": "",
            "risk_level": "",
            "suggestions": [],
            "report": ""
        }

        final_state = await self.graph.ainvoke(initial_state)
        return {
            "risk_level": final_state["risk_level"],
            "analysis":final_state["risk_analysis"],
            "suggestions":final_state["suggestions"],
            "report":final_state["report"]
        }

    def  build_graph(self):
        workflow = StateGraph(ContractState)

        """构建 LangGraph 工作流"""
        workflow = StateGraph(ContractState)
        workflow.add_node("parse", self.parse_document)
        workflow.add_node("analyze_risk", self.analyze_risk)
        workflow.add_node("generate_report", self.generate_report)
        workflow.set_entry_point("parse")
        workflow.add_edge("parse", "analyze_risk")
        workflow.add_edge("analyze_risk", "generate_report")
        workflow.add_edge("generate_report", END)
        return workflow.compile()

contract_agent = ContractAgent()
