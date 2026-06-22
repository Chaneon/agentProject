package com.agent.legal.model.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

@Data
public class ContractReviewRequest {
    @NotNull
    private MultipartFile file;
    /**
     * 合同名称，如：采购框架协议
     */
    private String contractName;
    /**
     * 签约相对方/对方公司名称
     */
    private String counterparty;
}
