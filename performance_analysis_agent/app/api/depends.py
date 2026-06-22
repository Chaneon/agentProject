from http.client import HTTPException
from typing import Dict, List

from fastapi import Depends

from app.core.db import get_redis, get_mysql_session
from app.core.security import SecurityManager
"""
依赖注入模块：为 API 提供统一的用户认证、权限校验和数据库会话。
FastAPI 的 Depends 机制会在路由函数执行前自动调用这些函数，并将返回值注入参数。
"""
# 全局安全管理器实例（单例）
security_manager = None

def init_security_manager():
    """初始化安全管理器，在应用启动时调用"""
    global security_manager
    redis_client = get_redis()
    db_session = get_mysql_session()
    security_manager = SecurityManager(redis_client, db_session)
    return security_manager

def get_security_manager()-> SecurityManager:
    """依赖注入：返回安全管理器实例"""
    if security_manager is None:
        init_security_manager()
    return security_manager

def get_current_user(request, security: SecurityManager = Depends(get_security_manager()))->Dict:
    """
    依赖注入：从请求头中提取 session_id，验证并返回用户信息。
    如果 session 无效或过期，抛出 401 异常。
    用户信息字典包含：user_id, role, org_id, visible_org_ids 等。
    """
    # 尝试从 Authorization header 获取 Bearer token
    session_id = request.headers.get("Authorization")
    if session_id and session_id.startswith("Bearer "):
        session_id = session_id[7:]
    else:
        # 否则从 X-Session-Id header 获取
        session_id = request.headers.get("X-Session-Id")
    if not session_id:
        raise HTTPException(status_code = 401, detail = "缺少会话标识")

    user_info = security.get_user_from_sesseion(session_id)
    if not user_info:
        raise HTTPException(status_code = 401, detail = "会话无效或已过期")

    # 将用户信息存到 request.state 中，方便后续使用
    request.state.user_info = user_info
    request.state.session_id = session_id
    return user_info

def get_user_visible_orgs(user_info: Dict = Depends(get_current_user()),
                          security: SecurityManager = Depends(get_security_manager()))->List[int]:
    """
    依赖注入：获取当前用户可见的机构ID列表。
    用于需要限制机构范围的查询接口。
    """
    org_ids = security.get_user_visible_org_ids(user_info["user_id"])
    if not org_ids:
        raise HTTPException(status_code = 403, detail = "用户未配置任何可见机构")
    return org_ids