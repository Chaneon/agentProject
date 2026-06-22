package com.agent.legal.config;

import cn.dev33.satoken.interceptor.SaInterceptor;
import cn.dev33.satoken.jwt.StpLogicJwtForSimple;
import cn.dev33.satoken.stp.StpLogic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Sa-Token 权限认证配置类
 * 负责配置 JWT 令牌风格和全局拦截器
 */
@Configuration
public class SaTokenConfig implements WebMvcConfigurer {
    /**
     * 配置 Sa-Token 的 JWT 风格为 Simple 模式
     *
     * @return StpLogic 实例，采用简单 JWT 模式（无状态）
     *
     * 说明：
     * - JWT 分为 Simple 和 Mixin 两种模式
     * - Simple 模式：仅包含用户 ID，无额外状态，适合纯无状态场景
     * - Mixin 模式：可包含 Session 数据，适合需要服务端状态的场景
     * - 这里使用 Simple 模式，配合 Token 自解析，无需 Redis 存储 Session
     */
    @Bean
    public StpLogic getStpLogicJwt() {
        return new StpLogicJwtForSimple();
    }
    /**
     * 注册全局拦截器，实现统一 Token 鉴权
     *
     * @param registry 拦截器注册器
     *
     * 拦截规则说明：
     * - 拦截路径：/** 所有接口
     * - 放行路径：/auth/login（登录接口）
     *           ：/error（错误页面，避免拦截影响错误响应）
     *
     * 工作原理：
     * SaInterceptor 会从请求头中读取 Token，验证有效性后注入当前会话上下文
     * 后续可通过 StpUtil.getLoginId() 获取当前登录用户 ID
     *
     * 注意：
     * - SaInterceptor 默认会配合 StpLogic 使用
     * - 如果 Token 无效或过期，会抛出 NotLoginException
     * - 放行的路径需要精确配置，否则会影响登录等公开接口
     */
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new SaInterceptor())
                .addPathPatterns("/**")    // 拦截所有请求
                .excludePathPatterns("/auth/login", "/error");  // 放行登录和错误路径
    }
}
