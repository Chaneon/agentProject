package com.agent.legal.controller;

import com.agent.legal.model.dto.ApiResponse;
import com.agent.legal.model.dto.LegalResearchRequest;
import com.agent.legal.model.entity.LegalResearch;
import com.agent.legal.service.LegalResearchService;
import com.agent.legal.utils.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.apache.catalina.security.SecurityUtil;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/research")
@RequiredArgsConstructor
public class LegalResearchController {
    private final LegalResearchService researchService;
    private final SecurityUtils securityUtils;

    @PostMapping("/query")
    public ApiResponse<LegalResearch> query(@Valid @RequestBody LegalResearchRequest request) {
        LegalResearch research = researchService.search(request, securityUtils.getCurrentUser());
        return ApiResponse.success(research);
    }

    @GetMapping("/{id}/report")
    public ApiResponse<LegalResearch> getReport(@PathVariable Integer id) {
        var user = securityUtils.getCurrentUser();
        LegalResearch research = researchService.getById(id, user.getUserId(), user.getRole().name());
        return ApiResponse.success(research);
    }

    @GetMapping("/history")
    public ApiResponse<List<LegalResearch>> getHistory() {
        List<LegalResearch> list = researchService.getHistory(securityUtils.getCurrentUserId());
        return ApiResponse.success(list);
    }
}
