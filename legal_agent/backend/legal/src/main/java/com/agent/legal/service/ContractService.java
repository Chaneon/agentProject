package com.agent.legal.service;

import com.agent.legal.mapper.ContractMapper;
import com.agent.legal.mapper.SysUserMapper;
import com.agent.legal.model.dto.ContractReviewRequest;
import com.agent.legal.model.entity.Contract;
import com.agent.legal.model.entity.SysUser;
import com.agent.legal.utils.FileUtils;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDateTime;

@Slf4j
@Service
@RequiredArgsConstructor
public class ContractService {

    private final ContractMapper contractMapper;

    private final AiProxyService aiProxyService;

    private final AuditService auditService;
    
    private final FileUtils fileUtils;

    public Contract uploadAndReview(ContractReviewRequest request, SysUser currentUser) throws Exception {
        MultipartFile file = request.getFile();
        String filePath = fileUtils.saveContractFile(file, currentUser.getUserId());

        Contract contract = new Contract();
        contract.setContractName(StringUtils.isNotBlank(request.getContractName()) ? request.getContractName() : file.getOriginalFilename());
        contract.setCounterparty(request.getCounterparty());
        contract.setFilePath(filePath);
        contract.setReviewStatus(Contract.ReviewStatus.IN_PROGRESS);
        contract.setCreatedBy(currentUser.getUserId());

        contract = contractMapper.save(contract);

        try{
            JsonNode aiResult= aiProxyService.reviewContract(file, contract.getContractName());
            String riskLevel = aiResult.path("risk_level").asText();

            contract.setRiskLevel(Contract.RiskLevel.valueOf(riskLevel));
            contract.setReviewReport(aiResult.toString());
            contract.setReviewStatus(Contract.ReviewStatus.COMPLETED);
            contract.setCreatedAt(LocalDateTime.now());
        } catch (Exception e){
            log.error("AI审查失败！", e);
            contract.setReviewStatus(Contract.ReviewStatus.PENDING);
            contract.setReviewReport("审查失败！"+e.getMessage());
        }
        contract = contractMapper.save(contract);
        auditService.log(currentUser.getUserId(), "CONTRACT_UPLOAD", "合同ID："+ contract.getContractId());

        return contract;
    }

    public  Contract getById(Integer contractId, Integer userId, String role){
        Contract contract = contractMapper.findById(contractId).orElseThrow(()->new RuntimeException("合同ID:"+contractId+"，不存在！"));

        if(!contract.getCreatedBy().equals(userId) && ! "admin".equals(role)) throw new RuntimeException("合同ID:"+contractId+"，无权限查看！");

        return contract;
    }

}
