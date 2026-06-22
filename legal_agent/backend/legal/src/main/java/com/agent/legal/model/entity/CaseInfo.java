package com.agent.legal.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 案件实体
 * 对应表：case
 */
@Data
@Entity
@Table(name = "case_info")
public class CaseInfo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "case_id")
    private Integer caseId;

    /**
     * 案件名称，如：张三诉李四合同纠纷
     */
    @Column(name = "case_name", length = 200, nullable = false)
    private String caseName;

    /**
     * 案号，如：(2025)沪01民初123号
     */
    @Column(name = "case_number", length = 100)
    private String caseNumber;

    /**
     * 客户/当事人名称
     */
    @Column(name = "client_name", length = 100)
    private String clientName;

    /**
     * 对方当事人/被告名称
     */
    @Column(name = "opposing_party", length = 100)
    private String opposingParty;

    /**
     * 案件状态：立案-刚立案，审理中-正在审理，已结案-已完结
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private CaseStatus status = CaseStatus.FILED;

    /**
     * 立案日期
     */
    @Column(name = "filing_date")
    private LocalDate filingDate;

    /**
     * 上诉截止日期，用于时效提醒
     */
    @Column(name = "deadline_appeal")
    private LocalDate deadlineAppeal;

    /**
     * 创建人ID，关联sys_user.user_id
     */
    @Column(name = "created_by", nullable = false)
    private Integer createdBy;

    /**
     * 创建时间
     */
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    /**
     * 更新时间
     */
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    /**
     * 案件状态枚举
     */
    public enum CaseStatus {
        FILED("立案"),
        IN_TRIAL("审理中"),
        CLOSED("已结案");

        private final String description;

        CaseStatus(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
