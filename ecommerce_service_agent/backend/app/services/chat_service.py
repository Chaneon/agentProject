
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.mysql import ChatSession, ChatMessage, TransferRecord
from app.agents.chat_agent import chat_agent
from app.services.memory_service import memory_service
from app.services.transfer_service import transfer_service
from app.utils.logger import log

"""
对话服务 - 核心业务逻辑
"""
class ChatService:
    """对话服务类"""

    async def process_message(
            self,
            db: Session,
            user_id: str,
            user_info: Dict,
            session_id: str,
            message: str,
            platform: str
    ) -> Dict[str, Any]:
        """处理用户消息"""
        # 1. 获取或创建会话
        session = self._get_or_create_session(db, session_id, user_id, platform)

        # 2. 保存用户消息
        user_msg = ChatMessage(session_id=session_id, role="user", content=message)
        db.add(user_msg)
        db.commit()

        # 3. 保存到短期记忆
        memory_service.save_short_term(session_id, "user", message)

        # 4. 获取工作记忆
        work_memory = memory_service.get_work_memory(session_id)

        # 5. 调用 Agent 生成回复
        agent_result = await chat_agent.process(
            message=message,
            user_id=user_id,
            user_info=user_info,
            session_id=session_id,
            work_memory=work_memory
        )

        # 6. 保存助手回复
        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=agent_result["reply"],
            intent=agent_result.get("intent"),
            emotion=agent_result.get("emotion")
        )
        db.add(assistant_msg)
        db.commit()

        # 7. 保存到短期记忆
        memory_service.save_short_term(session_id, "assistant", agent_result["reply"])

        # 8. 更新工作记忆
        if agent_result.get("work_memory_update"):
            memory_service.set_work_memory(
                session_id,
                agent_result["work_memory_update"]["state"],
                agent_result["work_memory_update"].get("data")
            )

        # 9. 检查转人工
        need_transfer = agent_result.get("need_transfer", False)
        if need_transfer:
            await self._trigger_transfer(db, session_id, user_id, agent_result.get("transfer_reason"))

        return {
            "reply": agent_result["reply"],
            "need_transfer": need_transfer,
            "session_id": session_id
        }

    def _get_or_create_session(self, db: Session, session_id: str, user_id: str, platform: str) -> ChatSession:
        """获取或创建会话"""
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            session = ChatSession(session_id=session_id, user_id=user_id, platform=platform)
            db.add(session)
            db.commit()
            db.refresh(session)
        return session

    async def _trigger_transfer(self, db: Session, session_id: str, user_id: str, reason: str):
        """触发转人工"""
        await transfer_service.add_to_queue(session_id, user_id, reason)
        db.query(ChatSession).filter(ChatSession.session_id == session_id).update({"status": "transferred"})
        db.commit()

    async def transfer_to_human(self, db: Session, session_id: str, user_id: str, reason: Optional[str]) -> Dict:
        """主动转人工"""
        await self._trigger_transfer(db, session_id, user_id, reason or "用户主动要求")
        return {"status": "queued", "queue_position": 0}


chat_service = ChatService()