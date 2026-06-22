-- 初始化 Agent 系统所需的 MySQL 表
-- 注意：user_org_visibility 表需要与 Java 系统同步或单独维护

CREATE TABLE IF NOT EXISTS chat_session (
    session_id VARCHAR(64) PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS chat_message (
    message_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    role ENUM('user','assistant','system') NOT NULL,
    agent_type ENUM('qa','simulation','report','knowledge'),
    content TEXT,
    extra_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_session_id (session_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS report_task (
    task_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    report_name VARCHAR(200) NOT NULL,
    report_params JSON,
    content_preview TEXT,
    status TINYINT DEFAULT 0,
    java_report_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_status (user_id, status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS simulation_record (
    sim_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    assumption JSON,
    target_metric VARCHAR(100),
    result_value DECIMAL(20,4),
    baseline_value DECIMAL(20,4),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS knowledge_document (
    doc_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(200),
    category VARCHAR(50),
    file_name VARCHAR(200),
    upload_user_id INT,
    status TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 示例：用户可见机构临时表（需要根据实际数据填充）
CREATE TABLE IF NOT EXISTS user_org_visibility (
                                                   id INT AUTO_INCREMENT PRIMARY KEY,
                                                   user_id INT NOT NULL,
                                                   visible_org_id INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入测试数据（示例）
INSERT INTO user_org_visibility (user_id, visible_org_id) VALUES (1, 100), (1, 101);