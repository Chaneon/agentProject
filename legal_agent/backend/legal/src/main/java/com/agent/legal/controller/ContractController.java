package com.agent.legal.controller;

import com.agent.legal.model.dto.ApiResponse;
import com.agent.legal.model.dto.ContractReviewRequest;
import com.agent.legal.model.entity.Contract;
import com.agent.legal.service.ContractService;
import com.agent.legal.utils.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.apache.catalina.security.SecurityUtil;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/contract")
@RequiredArgsConstructor
public class ContractController {
    private final ContractService contractService;
    private final SecurityUtils securityUtils;

    @PostMapping("/upload")
    public ApiResponse<Contract> upload(@Valid ContractReviewRequest request) throws Exception {
        Contract contract = contractService.uploadAndReview(request, securityUtils.getCurrentUser());
        return ApiResponse.success(contract);
    }

    @GetMapping("/{id}/review")
    public ApiResponse<Contract> getReviewResult(@PathVariable Integer id) {
        var user = securityUtils.getCurrentUser();
        Contract contract = contractService.getById(id, user.getUserId(), user.getRole().name());
        return ApiResponse.success(contract);
    }
}
