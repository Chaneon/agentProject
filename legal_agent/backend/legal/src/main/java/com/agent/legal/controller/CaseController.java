package com.agent.legal.controller;

import com.agent.legal.model.dto.ApiResponse;
import com.agent.legal.model.entity.CaseInfo;
import com.agent.legal.service.CaseService;
import com.agent.legal.utils.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.apache.catalina.security.SecurityUtil;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/case")
@RequiredArgsConstructor
public class CaseController {
    private final CaseService caseService;
    private final SecurityUtils securityUtils;

    @PostMapping
    public ApiResponse<CaseInfo> create(@Valid @RequestBody CaseInfo caseInfo) {
        CaseInfo saved = caseService.createCase(caseInfo, securityUtils.getCurrentUser());
        return ApiResponse.success(saved);
    }

    @PutMapping("/{id}")
    public ApiResponse<CaseInfo> update(@PathVariable Integer id, @Valid @RequestBody CaseInfo caseInfo) {
        CaseInfo updated = caseService.updateCase(id, caseInfo, securityUtils.getCurrentUser());
        return ApiResponse.success(updated);
    }

    @GetMapping("/{id}")
    public ApiResponse<CaseInfo> getDetail(@PathVariable Integer id) {
        var user = securityUtils.getCurrentUser();
        CaseInfo caseInfo = caseService.getById(id, user.getUserId(), user.getRole().name());
        return ApiResponse.success(caseInfo);
    }

    @GetMapping("/list")
    public ApiResponse<List<CaseInfo>> getList() {
        var user = securityUtils.getCurrentUser();
        List<CaseInfo> list = caseService.getList(user.getUserId(), user.getRole().name());
        return ApiResponse.success(list);
    }
}
