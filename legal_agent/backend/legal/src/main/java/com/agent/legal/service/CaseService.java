package com.agent.legal.service;

import com.agent.legal.mapper.CaseInfoMapper;
import com.agent.legal.model.entity.CaseInfo;
import com.agent.legal.model.entity.SysUser;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CaseService {
    private final CaseInfoMapper caseInfoMapper;
    private final AuditService auditService;

    public CaseInfo createCase(CaseInfo caseInfo, SysUser currentUser) {
        caseInfo.setCreatedBy(currentUser.getUserId());
        CaseInfo saved = caseInfoMapper.save(caseInfo);
        auditService.log(currentUser.getUserId(), "CASE_CREATE", "案件ID:" + saved.getCaseId());
        return saved;
    }

    public CaseInfo updateCase(Integer caseId, CaseInfo caseEntity, SysUser currentUser) {
        CaseInfo existing = caseInfoMapper.findById(caseId)
                .orElseThrow(() -> new RuntimeException("案件不存在"));
        if (!existing.getCreatedBy().equals(currentUser.getUserId()) && !"admin".equals(currentUser.getRole().name())) {
            throw new RuntimeException("无权修改");
        }
        existing.setCaseName(caseEntity.getCaseName());
        existing.setCaseNumber(caseEntity.getCaseNumber());
        existing.setClientName(caseEntity.getClientName());
        existing.setOpposingParty(caseEntity.getOpposingParty());
        existing.setStatus(caseEntity.getStatus());
        existing.setFilingDate(caseEntity.getFilingDate());
        existing.setDeadlineAppeal(caseEntity.getDeadlineAppeal());
        CaseInfo saved = caseInfoMapper.save(existing);
        auditService.log(currentUser.getUserId(), "CASE_UPDATE", "案件ID:" + saved.getCaseId());
        return saved;
    }

    public CaseInfo getById(Integer caseId, Integer userId, String role) {
        CaseInfo caseEntity = caseInfoMapper.findById(caseId)
                .orElseThrow(() -> new RuntimeException("案件不存在"));
        if (!caseEntity.getCreatedBy().equals(userId) && !"admin".equals(role)) {
            throw new RuntimeException("无权查看");
        }
        return caseEntity;
    }

    public List<CaseInfo> getList(Integer userId, String role) {
        if ("admin".equals(role)) {
            return caseInfoMapper.findAll();
        }
        return caseInfoMapper.findByCreatedBy(userId);
    }
}
