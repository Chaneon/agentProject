package com.agent.legal.mapper;

import com.agent.legal.model.entity.KnowledgeDoc;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface KnowledgeDocMapper extends JpaRepository<KnowledgeDoc, Integer> {
    //根据创建人（上传文件的人）查询
    List<KnowledgeDoc> findByUploadBy(Integer userId);
}
