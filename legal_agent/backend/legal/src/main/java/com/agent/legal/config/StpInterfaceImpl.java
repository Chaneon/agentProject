package com.agent.legal.config;

import cn.dev33.satoken.stp.StpInterface;
import com.agent.legal.mapper.SysUserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import java.util.ArrayList;
import java.util.List;

/**
 * Sa-Token 权限数据加载器（自定义权限校验接口）
 *
 * 作用：当 Sa-Token 需要校验用户角色或权限时，会回调此接口获取数据
 */
@Component
public class StpInterfaceImpl implements StpInterface{
    @Autowired
    private SysUserMapper sysUserMapper;
    /**
     * 获取当前登录用户的权限编码列表
     *
     * @param loginId  登录用户ID（即 StpUtil.getLoginId() 的值）
     * @param loginType 登录类型，如 'login'（支持多账号体系时区分）
     * @return 该用户拥有的权限编码集合
     */
    @Override
    public List<String> getPermissionList(Object loginId, String loginType) {
        // 目前未实现权限码管理，返回空集合
        // 如需实现，可查询权限表并返回如：["user:add", "contract:review", "doc:export"] 等
        return new ArrayList<>();
    }

    /**
     * 获取当前登录用户的角色列表
     *
     * @param loginId  登录用户ID（String 或 Integer 类型）
     * @param loginType 登录类型（如 'login'）
     * @return 该用户拥有的角色名称列表
     *
     * 逻辑说明：
     * 1. 将 loginId 转换为 Integer 类型作为用户ID
     * 2. 从数据库查询用户信息
     * 3. 将用户的角色枚举名称（如 "ADMIN"）添加到角色列表
     */
    @Override
    public List<String> getRoleList(Object loginId, String loginType) {
        List<String> roles = new ArrayList<>();
        // 将 loginId 转换为 Integer 类型（对应 sys_user 表中的 user_id）
        Integer userId = Integer.parseInt(loginId.toString());
        // 查询用户信息
        sysUserMapper.findById(userId).ifPresent(user -> roles.add(user.getRole().name()));
        return roles;
    }
}
