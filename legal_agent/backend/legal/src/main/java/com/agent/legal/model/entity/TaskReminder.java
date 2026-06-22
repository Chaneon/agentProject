package com.agent.legal.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 任务提醒实体
 * 对应表：task_reminder
 */
@Data
@Entity
@Table(name = "task_reminder")
public class TaskReminder {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "task_id")
    private Integer taskId;

    /**
     * 关联类型：case-案件，contract-合同
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "related_type", nullable = false)
    private RelatedType relatedType;

    /**
     * 关联的业务ID（case_id或contract_id）
     */
    @Column(name = "related_id", nullable = false)
    private Integer relatedId;

    /**
     * 任务标题，如：上诉截止日期提醒
     */
    @Column(name = "title", length = 200, nullable = false)
    private String title;

    /**
     * 截止日期/执行时间
     */
    @Column(name = "due_date", nullable = false)
    private LocalDateTime dueDate;

    /**
     * 是否已完成：TRUE-已完成，FALSE-待处理
     */
    @Column(name = "is_completed")
    private Boolean isCompleted = false;

    /**
     * 分配给哪个用户ID
     */
    @Column(name = "assigned_to", nullable = false)
    private Integer assignedTo;

    /**
     * 创建时间
     */
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    /**
     * 关联类型枚举
     */
    public enum RelatedType {
        CASE("case", "案件"),
        CONTRACT("contract", "合同");

        private final String code;
        private final String description;

        RelatedType(String code, String description) {
            this.code = code;
            this.description = description;
        }

        public String getCode() {
            return code;
        }

        public String getDescription() {
            return description;
        }
    }
}
