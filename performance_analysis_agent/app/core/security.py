import json
from typing import Optional, Dict, List

from redis import Redis
from sqlalchemy.orm import Session

from app.core.config import settings

class SecurityManager:
    def __init__(self, redis_client:Redis, db_session:Session):
        self.redis = redis_client
        self.db=db_session

    def get_user_from_sesseion(self, session_id:str) ->Optional[Dict]:
        key = f"session:{session_id}"
        data = self.redis.get(key)
        if not data:
            return None
        try:
            user_info = json.loads(data)
            return user_info
        except json.JSONDecodeError:
            return None

    def get_user_id(self, user_info:Dict):
        return user_info["user_id"]

    def get_user_visible_org_ids(self, user_id:int) ->List[int]:
        return None

    def can_access_global_data(self, user_info:Dict) -> bool:
        role = user_info.get("role", "").upper
        return role == settings.ROLE_MANAGER

    def apply_org_filter(self, user_info:Dict, sql:str) ->str:
        if self.can_access_global_data(user_info):
            visble_orgs = user_info.get("manage_org_ids", "")
            if visble_orgs:
                return self.inject_org_condition(str,user_info["user_id"])
            return sql
        else:
            visble_orgs = user_info.get("org_id")
            if not visble_orgs:
                raise PermissionError("用户未配置任何机构")
            return self.inject_org_condition(str,user_info["user_id"])


    def inject_org_condition(self,sql:str, user_id:int) -> str:
        sql_lower = sql.lower()
        sql_lower = f"select t1.* from ({sql})t1 left join (select * from view_user_manage_org where user_id={user_id}) t2 on  t1.org_id=t2.org_id "
        return sql_lower