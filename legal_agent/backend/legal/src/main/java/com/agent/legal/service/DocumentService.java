package com.agent.legal.service;

import com.agent.legal.mapper.GeneratedDocMapper;
import com.agent.legal.model.dto.DocGenRequest;
import com.agent.legal.model.entity.GeneratedDoc;
import com.agent.legal.model.entity.SysUser;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class DocumentService {
    private final GeneratedDocMapper generatedDocMapper;
    private final AiProxyService aiProxyService;
    private final AuditService auditService;

    public GeneratedDoc generate(DocGenRequest request, SysUser currentUser) {
        String content = aiProxyService.generateDocument(request.getDocType(), request.getFacts(), request.getClaims());
        GeneratedDoc doc = new GeneratedDoc();
        doc.setDocType(GeneratedDoc.DocType.valueOf(request.getDocType()));
        doc.setTitle(request.getTitle());
        doc.setContent(content);
        doc.setFinalVersion(content);
        doc.setCaseId(request.getCaseId());
        doc.setCreatedBy(currentUser.getUserId());
        doc = generatedDocMapper.save(doc);
        auditService.log(currentUser.getUserId(), "DOC_GENERATE", "文书ID:" + doc.getDocId());
        return doc;
    }

    public GeneratedDoc updateFinalVersion(Integer docId, String finalVersion, SysUser currentUser) {
        GeneratedDoc doc = generatedDocMapper.findById(docId)
                .orElseThrow(() -> new RuntimeException("文书不存在"));
        if (!doc.getCreatedBy().equals(currentUser.getUserId()) && !"admin".equals(currentUser.getRole().name())) {
            throw new RuntimeException("无权修改");
        }
        doc.setFinalVersion(finalVersion);
        return generatedDocMapper.save(doc);
    }

    public GeneratedDoc getById(Integer docId, Integer userId, String role) {
        GeneratedDoc doc = generatedDocMapper.findById(docId)
                .orElseThrow(() -> new RuntimeException("文书不存在"));
        if (!doc.getCreatedBy().equals(userId) && !"admin".equals(role)) {
            throw new RuntimeException("无权查看");
        }
        return doc;
    }

    public List<GeneratedDoc> getList(Integer userId) {
        return generatedDocMapper.findByCreatedBy(userId);
    }
}
