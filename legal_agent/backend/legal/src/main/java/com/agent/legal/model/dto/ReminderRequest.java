package com.agent.legal.model.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 任务提醒请求类
 */
@Data
public class ReminderRequest {
    /**
     * 关联类型
     */
    @NotBlank
    private String relatedType;
    /**
     *  关联的业务ID
     */
    @NotNull
    private Integer relatedId;
    /**
     * 任务标题
     */
    @NotBlank
    private String title;
    /**
     * 截止日期/执行时间
     */
    @NotNull
    private LocalDateTime dueDate;
}