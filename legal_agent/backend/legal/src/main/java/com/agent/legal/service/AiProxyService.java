package com.agent.legal.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

/**
 * AI 服务
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AiProxyService {

    private final RestTemplate restTemplate;

    @Value("${legal.ai.python-service-url}")
    private  String pythonUrl;


    /**
     * 调用 Python 服务进行合同审查
     */
    public JsonNode reviewContract(MultipartFile file, String contractName){
        try{
            // 1. 创建临时文件，保存上传的文件
            // 使用 .pdf 后缀，确保 Python 服务能正确解析文件类型
            Path tmpFile = Files.createTempFile("contract_", ".pdf");
            File file2 = tmpFile.toFile();
            file.transferTo(file2);
            // 2. 构建 multipart/form-data 请求体
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            // 添加文件（使用 FileSystemResource 包装）
            body.add("file", new FileSystemResource(file2));
            // 添加合同名称参数
            body.add("contract_name", contractName);

            // 3. 设置请求头
            HttpHeaders hearders = new HttpHeaders();
            hearders.setContentType(MediaType.MULTIPART_FORM_DATA);
            HttpEntity<MultiValueMap<String, Object>> entity = new HttpEntity<>(body, hearders);
            // 4. 发起post请求
            ResponseEntity<JsonNode> response = restTemplate.exchange(pythonUrl + "/api/contract/review", HttpMethod.POST, entity, JsonNode.class);

            // 5. 清理临时文件
            Files.deleteIfExists(tmpFile);
            return response.getBody();

        } catch (Exception e){
            throw  new RuntimeException("文件处理失败", e);
        }
    }

    /**
     * 调用 Python 服务进行法律检索
     */
    public JsonNode legalSearch(String query){
        try{
            // 1. 设置请求头
            HttpHeaders hearders = new HttpHeaders();
            hearders.setContentType(MediaType.APPLICATION_JSON);

            // 2. 设置请求体
            Map<String, String> request = new HashMap<>();
            request.put("query", query);
            HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, hearders);

            // 3. 发起post请求
            ResponseEntity<JsonNode> response = restTemplate.exchange(pythonUrl + "/api/legal/search", HttpMethod.POST, entity, JsonNode.class);

            return response.getBody();

        } catch (Exception e){
            throw  new RuntimeException("法律检索失败", e);
        }
    }

    /**
     * 调用 Python 服务生成法律文书
     */
    public String generateDocument(String  docType, String  facts, String claims){
        try{
            // 1. 设置请求头
            HttpHeaders hearders = new HttpHeaders();
            hearders.setContentType(MediaType.APPLICATION_JSON);

            // 2. 设置请求体
            Map<String, String> request = new HashMap<>();
            request.put("doc_type", docType);
            request.put("facts", facts);
            if (StringUtils.isNotBlank(claims)) request.put("claims", claims);
            HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, hearders);

            // 3. 发起post请求
            ResponseEntity<JsonNode> response = restTemplate.exchange(pythonUrl + "/api/doc/genrate", HttpMethod.POST, entity, JsonNode.class);

            // 4. 从响应中提取 content 字段（文书正文）
            return response.getBody().path("content").asText();

        } catch (Exception e){
            throw  new RuntimeException("文件生成失败", e);
        }
    }
}
