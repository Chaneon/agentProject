package com.agent.legal.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * 文书生成记录实体
 * 对应表：generated_doc
 */
@Data
@Entity
@Table(name = "generated_doc")
public class GeneratedDoc {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "doc_id")
    private Integer docId;

    /**
     * 文书类型：起诉状-民事诉讼起诉状，答辩状-应诉答辩状，律师函-律师函告，合同-草拟合同
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "doc_type", nullable = false)
    private DocType docType;

    /**
     * 文书标题
     */
    @Column(name = "title", length = 200, nullable = false)
    private String title;

    /**
     * AI生成的初稿内容（Markdown/富文本）
     */
    @Column(name = "content", columnDefinition = "LONGTEXT")
    private String content;

    /**
     * 用户确认后的最终版本
     */
    @Column(name = "final_version", columnDefinition = "LONGTEXT")
    private String finalVersion;

    /**
     * 关联的案件ID（可选）
     */
    @Column(name = "case_id")
    private Integer caseId;

    /**
     * 创建人ID
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
     * 文书类型枚举
     */
    public enum DocType {
        COMPLAINT("起诉状"),
        ANSWER("答辩状"),
        LAWYER_LETTER("律师函"),
        CONTRACT("合同");

        private final String description;

        DocType(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
