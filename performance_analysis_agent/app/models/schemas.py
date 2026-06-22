
from dataclasses import Field
from typing import Optional, Any, Dict, List
from pydantic import BaseModel
"""
  Pydantic 请求/响应模型，用于API请求和响应的数据校验和序列化
"""

class ChatRequest(BaseModel):
    # 统一对话请求
    session_id: str
    message: str= Field(..., max_length = 2000)   # 用户消息，最长不超过2000字符
    steam: bool = False                                 #是否流式响应

class ChatResponse(BaseModel):
    code: int = 200
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class SimulationRequest(BaseModel):
    # 模拟测算请求
    session_id: str
    assumption : Optional[Dict[str, Any]] = None    #假设条件，如 deposit_rate_delta_bp:10
    target_metric:str                               #目标指标，如 net_profit
    instruction:Optional[str] = None                #自然语言描述

class SimulationResponse(BaseModel):
    baseline:float
    result:float
    change:float
    change_percent:float

class ReportGenerateRequest(BaseModel):
    # 报表生成请求
    session_id: str
    instruction: str                                            #生成指令，如：生成本地度耕支行存款业绩排行榜
    report_name: str = Field(..., max_length = 200)     # 报表名称

class ReportGenerateResponse(BaseModel):
    task_id: int
    status: str # processing、success、failed

class KnowledgeAskRequest(BaseModel):
    session_id: str
    question: str = Field(..., max_length = 500)

class KnowledgeAskResponse(BaseModel):
    answer: str
    sources: List[str]  #引用来源（文档id列表）