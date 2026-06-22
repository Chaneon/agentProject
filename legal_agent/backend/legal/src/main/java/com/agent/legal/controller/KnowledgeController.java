package com.agent.legal.controller;

import com.agent.legal.model.dto.ApiResponse;
import com.agent.legal.model.entity.KnowledgeDoc;
import com.agent.legal.service.KnowledgeService;
import com.agent.legal.utils.SecurityUtils;
import lombok.RequiredArgsConstructor;
import org.apache.catalina.security.SecurityUtil;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/knowledge")
@RequiredArgsConstructor
public class KnowledgeController {
    private final KnowledgeService knowledgeService;
    private final SecurityUtils securityUtils;

    @PostMapping("/upload")
    public ApiResponse<KnowledgeDoc> upload(@RequestParam("file") MultipartFile file) throws Exception {
        KnowledgeDoc doc = knowledgeService.upload(file, securityUtils.getCurrentUser());
        return ApiResponse.success(doc);
    }

    @DeleteMapping("/{id}")
    public ApiResponse<Void> delete(@PathVariable Integer id) throws Exception {
        knowledgeService.delete(id, securityUtils.getCurrentUser());
        return ApiResponse.success(null);
    }

    @GetMapping("/list")
    public ApiResponse<List<KnowledgeDoc>> getList() {
        var user = securityUtils.getCurrentUser();
        List<KnowledgeDoc> list = knowledgeService.getList(user.getUserId(), user.getRole().name());
        return ApiResponse.success(list);
    }
}
