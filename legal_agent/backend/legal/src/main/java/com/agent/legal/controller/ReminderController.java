package com.agent.legal.controller;

import com.agent.legal.model.dto.ApiResponse;
import com.agent.legal.model.dto.ReminderRequest;
import com.agent.legal.model.entity.TaskReminder;
import com.agent.legal.service.ReminderService;
import com.agent.legal.utils.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.apache.catalina.security.SecurityUtil;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/reminder")
@RequiredArgsConstructor
public class ReminderController {
    private final ReminderService reminderService;
    private final SecurityUtils securityUtils;

    @PostMapping
    public ApiResponse<TaskReminder> create(@Valid @RequestBody ReminderRequest request) {
        TaskReminder reminder = reminderService.createReminder(request, securityUtils.getCurrentUser());
        return ApiResponse.success(reminder);
    }

    @GetMapping("/unfinished")
    public ApiResponse<List<TaskReminder>> getUnfinished() {
        List<TaskReminder> list = reminderService.getUnfinished(securityUtils.getCurrentUserId());
        return ApiResponse.success(list);
    }

    @PutMapping("/{id}/complete")
    public ApiResponse<Void> complete(@PathVariable Integer id) {
        reminderService.markCompleted(id, securityUtils.getCurrentUser());
        return ApiResponse.success(null);
    }
}
