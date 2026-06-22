-- ============================================================
-- 电商智能客服Agent - MySQL 初始化脚本
-- 只创建 Agent 自己维护的表
-- ============================================================

CREATE DATABASE IF NOT EXISTS ecommerce_cs
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ecommerce_cs;

-- 会话表
CREATE TABLE chat_session (
                              session_id VARCHAR(64) PRIMARY KEY,
                              user_id VARCHAR(64) NOT NULL,
                              platform VARCHAR(20) NOT NULL,
                              status ENUM('active', 'closed', 'transferred') DEFAULT 'active',
                              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                              updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                              INDEX idx_user_id (user_id),
                              INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 消息表
CREATE TABLE chat_message (
                              message_id BIGINT PRIMARY KEY AUTO_INCREMENT,
                              session_id VARCHAR(64) NOT NULL,
                              role ENUM('user', 'assistant', 'agent') NOT NULL,
                              content TEXT NOT NULL,
                              intent VARCHAR(20),
                              emotion VARCHAR(20),
                              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                              INDEX idx_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 对话摘要表
CREATE TABLE conversation_summary (
                                      summary_id INT PRIMARY KEY AUTO_INCREMENT,
                                      user_id VARCHAR(64) NOT NULL,
                                      session_id VARCHAR(64) NOT NULL,
                                      summary_text TEXT,
                                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                                      INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 转接记录表
CREATE TABLE transfer_record (
                                 transfer_id INT PRIMARY KEY AUTO_INCREMENT,
                                 session_id VARCHAR(64) NOT NULL,
                                 agent_id VARCHAR(64) NOT NULL,
                                 reason VARCHAR(100),
                                 context JSON,
                                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                                 resolved_at DATETIME,
                                 INDEX idx_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;