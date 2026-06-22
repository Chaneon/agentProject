package com.agent.legal.mapper;

import com.agent.legal.model.entity.GeneratedDoc;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface GeneratedDocMapper extends JpaRepository<GeneratedDoc, Integer> {
    //根据创建人查询
    List<GeneratedDoc> findByCreatedBy(Integer userId);
}
