package com.agent.legal.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 系统用户实体
 * 对应表：sys_user
 */
@Data
@Entity
@Table(name = "sys_user")
public class SysUser {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Integer userId;

    /**
     * 登录用户名，唯一
     */
    @Column(name = "username", length = 50, nullable = false, unique = true)
    private String username;

    /**
     * 加密后的密码（BCrypt）
     */
    @Column(name = "password_hash", length = 255, nullable = false)
    private String passwordHash;

    /**
     * 真实姓名，如：张三律师
     */
    @Column(name = "real_name", length = 50)
    private String realName;

    /**
     * 用户角色：admin-系统管理员，lawyer-律师，paralegal-法务助理
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false)
    private UserRole role = UserRole.lawyer;

    /**
     * 所属机构ID，关联组织架构表（预留）
     */
    @Column(name = "org_id")
    private Integer orgId;

    /**
     * 创建时间
     */
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    /**
     * 用户角色枚举
     */
    public enum UserRole {
        admin("系统管理员"),
        lawyer("律师"),
        paralegal("法务助理");

        private final String description;

        UserRole(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
