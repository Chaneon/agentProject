package com.agent.legal.mapper;

import com.agent.legal.model.entity.CaseInfo;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CaseInfoMapper extends JpaRepository< CaseInfo, Integer> {
    //根据创建人查询
    List<CaseInfo> findByCreatedBy(Integer userId);
    //根据状态查询
    List< CaseInfo> findByStatus( CaseInfo.CaseStatus status);
}
