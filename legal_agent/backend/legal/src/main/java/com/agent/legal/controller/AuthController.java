package com.agent.legal.controller;

import cn.dev33.satoken.stp.SaLoginModel;
import cn.dev33.satoken.stp.StpUtil;
import com.agent.legal.mapper.SysUserMapper;
import com.agent.legal.model.dto.ApiResponse;
import com.agent.legal.model.dto.LoginRequest;
import com.agent.legal.model.dto.LoginResponse;
import com.agent.legal.model.entity.SysUser;
import com.agent.legal.utils.SecurityUtils;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.apache.catalina.security.SecurityUtil;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {
    private final SysUserMapper sysUserMapper;
    private final SecurityUtils securityUtils;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @PostMapping("/login")
    public ApiResponse<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        SysUser user = sysUserMapper.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("用户名或密码错误"));
        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new RuntimeException("用户名或密码错误");
        }
        StpUtil.login(user.getUserId(), new SaLoginModel().setTimeout(43200));
        String token = StpUtil.getTokenValue();
        return ApiResponse.success(new LoginResponse(token, user.getUsername(), user.getRealName(),
                user.getRole().name(), StpUtil.getTokenTimeout()));
    }

    @PostMapping("/logout")
    public ApiResponse<Void> logout() {
        StpUtil.logout();
        return ApiResponse.success(null);
    }

    @GetMapping("/profile")
    public ApiResponse<SysUser> profile() {
        SysUser user = securityUtils.getCurrentUser();
        user.setPasswordHash(null);
        return ApiResponse.success(user);
    }
}
