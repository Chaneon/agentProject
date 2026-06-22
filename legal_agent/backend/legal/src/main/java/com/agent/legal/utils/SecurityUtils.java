package com.agent.legal.utils;

import cn.dev33.satoken.stp.StpUtil;
import com.agent.legal.mapper.SysUserMapper;
import com.agent.legal.model.entity.SysUser;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
public class SecurityUtils {

    @Autowired
    private SysUserMapper sysUserMapper;

    public Integer getCurrentUserId() {
        return Integer.parseInt(StpUtil.getLoginId().toString());
    }

    public SysUser getCurrentUser() {
        return sysUserMapper.findById(getCurrentUserId()).orElse(null);
    }
}
