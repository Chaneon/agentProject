package com.agent.legal.utils;

import cn.hutool.core.lang.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Component
public class FileUtils {

    @Value("${legal.ai.file-upload-path}")
    private String uploadPath;
    
    /**
     * 保存合同文件
     */
    public String saveContractFile(MultipartFile file, Integer userId) throws IOException {
       return saveFile(file, userId, "contracts");
    }

    /**
     *保存知识库文件
     */
    public String saveKnowledgeFile(MultipartFile file, Integer userId) throws IOException {
        return saveFile(file, userId, "knowledge");
    }

    /**
     * 删除文件
     */
    public void deleteFile(String filePath) throws IOException {
        Files.deleteIfExists(Paths.get(filePath));
    }


    private String saveFile(MultipartFile file, Integer userId, String fileType) throws IOException {
        String originalName = file.getOriginalFilename();
        String ext = originalName.substring(originalName.lastIndexOf("."));
        String newFileName = UUID.randomUUID() + ext;
        Path dir = Paths.get(uploadPath, fileType, userId.toString());
        if (!Files.exists(dir)) Files.createDirectories(dir);
        Path filePath = dir.resolve(newFileName);
        file.transferTo(filePath.toFile());
        return filePath.toString();
    }
}
