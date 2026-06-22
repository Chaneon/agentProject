package com.agent.legal.model.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * 登录响应类
 */
@Data
@AllArgsConstructor
public class LoginResponse {
    /**
     *  JWT 访问令牌
     */
    private String token;
    /**
     * 登录用户名
     */
    private String username;
    /**
     * 用户真实姓名
     */
    private String realName;
    /**
     * 用户角色
     */
    private String role;
    /**
     * token有效期
     */
    private Long expiresIn;
}