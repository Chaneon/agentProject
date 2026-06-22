package com.agent.legal.service;

import com.agent.legal.mapper.AuditLogMapper;
import com.agent.legal.model.entity.AuditLog;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditService {
    private AuditLogMapper auditLogMapper;

    public void log(Integer userId, String action,String detail){
        AuditLog log = new AuditLog();
        log.setUserId(userId);
        log.setAction(action);
        log.setDetail(detail);
        auditLogMapper.save(log);
    }
}
