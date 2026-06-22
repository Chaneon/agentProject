package com.agent.legal.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 法律研究记录实体
 * 对应表：legal_research
 */
@Data
@Entity
@Table(name = "legal_research")
public class LegalResearch {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "research_id")
    private Integer researchId;

    /**
     * 用户输入的自然语言查询，如：民法典第577条违约金适用规则
     */
    @Column(name = "query_text", nullable = false, columnDefinition = "TEXT")
    private String queryText;

    /**
     * 检索到的相关法条列表（JSON数组）
     */
    @Column(name = "retrieved_laws", columnDefinition = "JSON")
    private String retrievedLaws;

    /**
     * 检索到的相关案例列表（类案）
     */
    @Column(name = "retrieved_cases", columnDefinition = "JSON")
    private String retrievedCases;

    /**
     * AI生成的类案分析报告（Markdown/HTML格式）
     */
    @Column(name = "generated_report", columnDefinition = "TEXT")
    private String generatedReport;

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
}
