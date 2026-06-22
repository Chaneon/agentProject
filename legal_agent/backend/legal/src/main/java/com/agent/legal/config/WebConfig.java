package com.agent.legal.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * Web 全局配置类
 *
 * 配置跨域资源共享（CORS），允许前端应用（如 Vue 项目）跨域访问后端 API
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        //跨域配置
        registry.addMapping("/**") // 所有接口路径
                .allowedOrigins("*")    // 允许所有域名访问（开发环境）
                .allowedMethods("*")    // 允许所有 HTTP 方法（GET、POST、PUT、DELETE 等）
                .allowedHeaders("*");   // 允许所有请求头（Authorization、Content-Type 等）
    }
}