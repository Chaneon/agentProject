package com.agent.legal.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 知识库文档实体
 * 对应表：knowledge_doc
 */
@Data
@Entity
@Table(name = "knowledge_doc")
public class KnowledgeDoc {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "doc_id")
    private Integer docId;

    /**
     * 文档名称，如：劳动合同模板_v2.docx
     */
    @Column(name = "doc_name", length = 200, nullable = false)
    private String docName;

    /**
     * 文档存储路径
     */
    @Column(name = "file_path", length = 500)
    private String filePath;

    /**
     * 向量化状态：未向量化-待处理，已向量化-已存入Milvus
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "vector_status")
    private VectorStatus vectorStatus = VectorStatus.NOT_VECTORIZED;

    /**
     * 上传人ID
     */
    @Column(name = "upload_by", nullable = false)
    private Integer uploadBy;

    /**
     * 创建时间
     */
    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    /**
     * 向量化状态枚举
     */
    public enum VectorStatus {
        NOT_VECTORIZED("未向量化"),
        VECTORIZED("已向量化");

        private final String description;

        VectorStatus(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
