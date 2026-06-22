package com.agent.legal.mapper;

import com.agent.legal.model.entity.AuditLog;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AuditLogMapper extends JpaRepository<AuditLog, Long> {
}
