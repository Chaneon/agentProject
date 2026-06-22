package com.agent.legal.service;

import com.agent.legal.mapper.KnowledgeDocMapper;
import com.agent.legal.model.entity.KnowledgeDoc;
import com.agent.legal.model.entity.SysUser;
import com.agent.legal.utils.FileUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class KnowledgeService {
    private final KnowledgeDocMapper knowledgeDocMapper;
    private final FileUtils fileUtils;
    private final AuditService auditService;

    public KnowledgeDoc upload(MultipartFile file, SysUser currentUser) throws IOException {
        String filePath = fileUtils.saveKnowledgeFile(file, currentUser.getUserId());
        KnowledgeDoc doc = new KnowledgeDoc();
        doc.setDocName(file.getOriginalFilename());
        doc.setFilePath(filePath);
        doc.setUploadBy(currentUser.getUserId());
        doc = knowledgeDocMapper.save(doc);
        auditService.log(currentUser.getUserId(), "KNOWLEDGE_UPLOAD", "文档ID:" + doc.getDocId());
        // TODO: 触发异步向量化任务（可调用 Python 服务）
        return doc;
    }

    public void delete(Integer docId, SysUser currentUser) throws IOException {
        KnowledgeDoc doc = knowledgeDocMapper.findById(docId)
                .orElseThrow(() -> new RuntimeException("文档不存在"));
        if (!doc.getUploadBy().equals(currentUser.getUserId()) && !"admin".equals(currentUser.getRole().name())) {
            throw new RuntimeException("无权删除");
        }
        fileUtils.deleteFile(doc.getFilePath());
        knowledgeDocMapper.delete(doc);
        auditService.log(currentUser.getUserId(), "KNOWLEDGE_DELETE", "文档ID:" + docId);
    }

    public List<KnowledgeDoc> getList(Integer userId, String role) {
        if ("admin".equals(role)) {
            return knowledgeDocMapper.findAll();
        }
        return knowledgeDocMapper.findByUploadBy(userId);
    }
}
