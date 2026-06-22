package com.agent.legal.service;

import com.agent.legal.mapper.LegalResearchMapper;
import com.agent.legal.model.dto.LegalResearchRequest;
import com.agent.legal.model.entity.LegalResearch;
import com.agent.legal.model.entity.SysUser;
import com.fasterxml.jackson.databind.JsonNode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class LegalResearchService {
    private final LegalResearchMapper legalResearchMapper;
    private final AiProxyService aiProxyService;
    private final AuditService auditService;

    public LegalResearch search(LegalResearchRequest request, SysUser currentUser) {
        LegalResearch research = new LegalResearch();
        research.setQueryText(request.getQuery());
        research.setCreatedBy(currentUser.getUserId());
        research = legalResearchMapper.save(research);

        try {
            JsonNode aiResult = aiProxyService.legalSearch(request.getQuery());
            research.setRetrievedLaws(aiResult.path("laws").toString());
            research.setRetrievedCases(aiResult.path("cases").toString());
            research.setGeneratedReport(aiResult.path("report").asText());
            research = legalResearchMapper.save(research);
            auditService.log(currentUser.getUserId(), "LEGAL_RESEARCH", "研究ID:" + research.getResearchId());
        } catch (Exception e) {
            log.error("法律研究失败", e);
            research.setGeneratedReport("研究失败：" + e.getMessage());
            research = legalResearchMapper.save(research);
        }
        return research;
    }

    public LegalResearch getById(Integer researchId, Integer userId, String role) {
        LegalResearch research = legalResearchMapper.findById(researchId)
                .orElseThrow(() -> new RuntimeException("记录不存在"));
        if (!research.getCreatedBy().equals(userId) && !"admin".equals(role)) {
            throw new RuntimeException("无权查看");
        }
        return research;
    }

    public List<LegalResearch> getHistory(Integer userId) {
        return legalResearchMapper.findByCreatedByOrderByCreatedAtDesc(userId);
    }
}
