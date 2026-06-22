package com.agent.legal.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * 合同实体
 * 对应表：contract
 */
@Data
@Entity
@Table(name = "contract")
public class Contract {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "contract_id")
    private Integer contractId;

    /**
     * 合同名称，如：采购框架协议
     */
    @Column(name = "contract_name", length = 200, nullable = false)
    private String contractName;

    /**
     * 签约相对方/对方公司名称
     */
    @Column(name = "counterparty", length = 200)
    private String counterparty;

    /**
     * 合同文件存储路径（相对路径）
     */
    @Column(name = "file_path", length = 500)
    private String filePath;

    /**
     * 审查状态：待审查-等待AI审查，审查中-正在处理，已完成-审查报告已生成
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "review_status")
    private ReviewStatus reviewStatus = ReviewStatus.PENDING;

    /**
     * 综合风险等级：高-需重点关注，中-存在一般风险，低-风险可控
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "risk_level")
    private RiskLevel riskLevel;

    /**
     * AI生成的审查报告内容（JSON或纯文本）
     */
    @Column(name = "review_report", columnDefinition = "TEXT")
    private String reviewReport;

    /**
     * 上传人/创建人ID
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
     * 审查状态枚举
     */
    public enum ReviewStatus {
        PENDING("待审查"),
        IN_PROGRESS("审查中"),
        COMPLETED("已完成");

        private final String description;

        ReviewStatus(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }

    /**
     * 风险等级枚举
     */
    public enum RiskLevel {
        HIGH("高"),
        MEDIUM("中"),
        LOW("低");

        private final String description;

        RiskLevel(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
