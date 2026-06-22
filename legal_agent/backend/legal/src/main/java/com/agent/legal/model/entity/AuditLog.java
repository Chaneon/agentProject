package com.agent.legal.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 操作审计日志实体
 * 对应表：audit_log
 */
@Data
@Entity
@Table(name = "audit_log")
public class AuditLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "log_id")
    private Long logId;

    /**
     * 操作用户ID
     */
    @Column(name = "user_id", nullable = false)
    private Integer userId;

    /**
     * 操作类型，如：UPLOAD_CONTRACT, GENERATE_DOC
     */
    @Column(name = "action", length = 100, nullable = false)
    private String action;

    /**
     * 操作详情（JSON格式，含请求参数、结果摘要）
     */
    @Column(name = "detail", columnDefinition = "JSON")
    private String detail;

    /**
     * 客户端IP地址（支持IPv4/IPv6）
     */
    @Column(name = "ip_address", length = 45)
    private String ipAddress;

    /**
     * 操作时间
     */
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
