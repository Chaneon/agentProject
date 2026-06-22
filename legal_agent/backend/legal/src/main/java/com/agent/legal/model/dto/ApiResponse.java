package com.agent.legal.model.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * 统一 API 响应结果封装类
 * @param <T>
 */
@Data
@AllArgsConstructor
public class ApiResponse<T> {
    /**
     * 响应状态码
     */
    private int code;
    /**
     * 响应消息（成功时为 "success"，失败时为具体错误描述）
     */
    private String message;
    /**
     * 响应数据（成功时返回业务数据，失败时为 null）
     */
    private T data;

    /**
     * 成功响应（状态码 200，消息 "success"）
     */
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(200, "success", data);
    }
    /**
     * 失败响应（状态码 500，自定义错误信息）
     */
    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(500, message, null);
    }
    /**
     * 失败响应（自定义状态码和错误信息）
     */
    public static <T> ApiResponse<T> error(int code, String message) {
        return new ApiResponse<>(code, message, null);
    }
}