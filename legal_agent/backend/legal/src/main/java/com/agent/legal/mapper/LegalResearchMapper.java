package com.agent.legal.mapper;

import com.agent.legal.model.entity.LegalResearch;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface LegalResearchMapper extends JpaRepository<LegalResearch, Integer> {
    //根据创建人查询，根据创建日期降序
    List<LegalResearch> findByCreatedByOrderByCreatedAtDesc(Integer userId);
}
