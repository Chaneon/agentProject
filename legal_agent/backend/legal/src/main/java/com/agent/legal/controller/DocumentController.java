package com.agent.legal.controller;

import com.agent.legal.model.dto.ApiResponse;
import com.agent.legal.model.dto.DocGenRequest;
import com.agent.legal.model.entity.GeneratedDoc;
import com.agent.legal.service.DocumentService;
import com.agent.legal.utils.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.apache.catalina.security.SecurityUtil;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/doc")
@RequiredArgsConstructor
public class DocumentController {
    private final DocumentService documentService;
    private final SecurityUtils securityUtils;

    @PostMapping("/generate")
    public ApiResponse<GeneratedDoc> generate(@Valid @RequestBody DocGenRequest request) {
        GeneratedDoc doc = documentService.generate(request, securityUtils.getCurrentUser());
        return ApiResponse.success(doc);
    }

    @PutMapping("/{id}")
    public ApiResponse<GeneratedDoc> updateFinal(@PathVariable Integer id, @RequestBody String finalVersion) {
        var user = securityUtils.getCurrentUser();
        GeneratedDoc doc = documentService.updateFinalVersion(id, finalVersion, user);
        return ApiResponse.success(doc);
    }

    @GetMapping("/{id}")
    public ApiResponse<GeneratedDoc> getDetail(@PathVariable Integer id) {
        var user = securityUtils.getCurrentUser();
        GeneratedDoc doc = documentService.getById(id, user.getUserId(), user.getRole().name());
        return ApiResponse.success(doc);
    }

    @GetMapping("/list")
    public ApiResponse<List<GeneratedDoc>> getList() {
        List<GeneratedDoc> list = documentService.getList(securityUtils.getCurrentUserId());
        return ApiResponse.success(list);
    }
}
