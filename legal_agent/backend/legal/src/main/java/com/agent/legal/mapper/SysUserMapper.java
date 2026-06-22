package com.agent.legal.mapper;

import com.agent.legal.model.entity.SysUser;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface SysUserMapper extends JpaRepository<SysUser, Integer> {
    //根据名称查询
    Optional<SysUser> findByUsername(String username);
    //根据名称判断是否已存在
    boolean existsByUsername(String username);
}
