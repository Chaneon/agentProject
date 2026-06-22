from app.core.security import SecurityManager

"""
权限过滤器：对 SQL 语句添加机构权限条件。
实际直接复用 SecurityManager 的方法，此处仅做封装。
"""
class PermissionFilter:
    def __init__(self, security_manager: SecurityManager):
        self.security - security_manager

    def add_org_constraint(self, sql: str, user_info: dict) -> str:
        return self.security.apply_org_filter(user_info, sql)