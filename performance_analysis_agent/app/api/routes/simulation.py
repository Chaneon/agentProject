import datetime
from http.client import HTTPException
from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.simulation_agent import SimulationAgent
from app.api.depends import get_current_user
from app.core.db import get_mysql_session
from app.models.mysql import SimulationRecord
from app.models.schemas import SimulationRequest, SimulationResponse
"""
模拟测算独立接口：接收假设条件或自然语言描述，调用存储过程引擎计算影响。
"""
router = APIRouter(prefix="/simulation", tags = ["模拟测算"])

@router.post("/calculate", response_model=SimulationResponse)
async def calculate_simulation(
        req: SimulationRequest,
        user_info:Dict= Depends(get_current_user()),
        db:Session = Depends(get_mysql_session())):
    """
    执行模拟测算：
    - 如果没有提供 instruction，则使用 assumption 中的描述（兼容旧版）
    - 创建 SimulationAgent 实例，调用其 process 方法
    - 保存测算记录到数据库
    - 返回测算结果（baseline, result, change, change_percent）
    """
    agent = SimulationAgent(user_info)
    try:
        # 构造用户消息：如果 instruction 为空，则从 assumption 中提取描述
        user_message = req.instruction or f"假设条件：{req.instruction}，测算指标：{req.target_metric}"
        result = await agent.process(user_message, user_info)
        # 从结果中提取数值（假设存储过程返回的第一行第一列为影响值）
        extra = result.get("extra", {})
        raw = extra.get("raw_result", {})
        rows = raw.get("rows", [])
        impact_value = rows[0][0] if rows else 0.0
        # 保存测算记录到数据库
        record = SimulationRecord(
            user_id = user_info["user_id"],
            assumption = req.assumption,
            target_metric = req.target_metric,
            result_value = impact_value,
            baseline_value = 0.0,               # 基准值由存储过程内部计算，这里暂不处理
            created_date = datetime.now()
        )
        db.add(record)
        db.commit()
        # 构造响应
        return  SimulationResponse(
            baseline = 0.0,
            result = impact_value,
            change = impact_value,
            change_percent=0.0
        )
    except Exception as e:
        raise  HTTPException(status_code=400, detail = str(e))
    finally:
        agent.close()