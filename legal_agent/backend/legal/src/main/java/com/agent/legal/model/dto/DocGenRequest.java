package com.agent.legal.model.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 文书生成请求参数类
 */
@Data
public class DocGenRequest {
    /**
     * 文书类型：起诉状-民事诉讼起诉状，答辩状-应诉答辩状，律师函-律师函告，合同-草拟合同
     */
    @NotBlank
    private String docType;
    /**
     * 文书标题
     */
    @NotBlank
    private String title;
    /**
     * 案件基本事实描述
     */
    @NotBlank
    private String facts;
    /**
     * 诉讼请求/诉求内容
     */
    private String claims;
    /**
     * 关联的案件ID（可选）
     */
    private Integer caseId;
}