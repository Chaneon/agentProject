from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from app.agents.report_agent import ReportAgent
from app.api.depends import get_current_user
from app.core.db import get_mysql_session
from app.models.schemas import ReportGenerateRequest, ReportGenerateResponse
"""
报告生成接口：根据用户指令生成报表，并在后台异步执行，返回任务ID。
"""
router = APIRouter(prefix="/report", tags = ["报告生成"])

@router.post("/generate", response_model=ReportGenerateResponse)
async def generate_report(
        req: ReportGenerateRequest,
        background_tasks: BackgroundTasks,
        user_info:Dict= Depends(get_current_user()),
        db:Session = Depends(get_mysql_session())):
    """
        提交报告生成任务：
        - 立即创建一条报告任务记录（状态为 processing）
        - 将实际的生成逻辑放入后台任务执行，避免阻塞
        - 返回任务ID，前端可轮询查询结果
        """
    agent = ReportAgent(db, user_info)
    # 创建任务记录，返回 task_id
    task_id = agent.create_report_task(report_name=req.report_name, instruction=req.instruction)
    # 将耗时操作加入后台任务队列
    background_tasks.add_task(
        agent.generate_and_save,
        task_id =task_id,
        instruction=req.instruction,
        report_name=req.report_name
    )

    return ReportGenerateResponse(task_id = task_id, status= "processing")