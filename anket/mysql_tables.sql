-- ============================================================
-- Sustainage Anket Sistemi - MySQL Veritabanı Şeması
-- Plesk Panel için (sustainageksp_)
-- Tarih: 2025-10-23
-- ============================================================

-- 1. ANKETLER TABLOSU
CREATE TABLE IF NOT EXISTS surveys (
    survey_id INT AUTO_INCREMENT PRIMARY KEY,
    survey_name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    survey_type VARCHAR(50) DEFAULT 'materiality',
    description TEXT,
    created_date DATETIME NOT NULL,
    deadline_date DATE NOT NULL,
    status ENUM('active', 'closed', 'draft') DEFAULT 'active',
    unique_token VARCHAR(64) UNIQUE NOT NULL,
    api_key VARCHAR(128) NOT NULL,
    response_count INT DEFAULT 0,
    created_by VARCHAR(100),
    updated_date DATETIME,
    INDEX idx_token (unique_token),
    INDEX idx_status (status),
    INDEX idx_created (created_date DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. ANKET KONULARI TABLOSU
CREATE TABLE IF NOT EXISTS survey_topics (
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT NOT NULL,
    topic_code VARCHAR(50) NOT NULL,
    topic_name VARCHAR(255) NOT NULL,
    topic_category VARCHAR(100),
    description TEXT,
    display_order INT DEFAULT 0,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id) ON DELETE CASCADE,
    INDEX idx_survey (survey_id),
    INDEX idx_code (topic_code),
    INDEX idx_order (survey_id, display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. ANKET YANITLARI TABLOSU
CREATE TABLE IF NOT EXISTS survey_responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT NOT NULL,
    stakeholder_name VARCHAR(255) NOT NULL,
    stakeholder_email VARCHAR(255) NOT NULL,
    stakeholder_organization VARCHAR(255),
    stakeholder_role VARCHAR(100),
    topic_code VARCHAR(50) NOT NULL,
    importance_score TINYINT NOT NULL,
    impact_score TINYINT NOT NULL,
    comment TEXT,
    submitted_date DATETIME NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id) ON DELETE CASCADE,
    INDEX idx_survey (survey_id),
    INDEX idx_topic (topic_code),
    INDEX idx_email (stakeholder_email),
    INDEX idx_date (submitted_date DESC),
    CHECK (importance_score BETWEEN 1 AND 5),
    CHECK (impact_score BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. API LOG TABLOSU
CREATE TABLE IF NOT EXISTS api_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    api_key VARCHAR(128) NOT NULL,
    action VARCHAR(100) NOT NULL,
    request_data TEXT,
    response_data TEXT,
    status_code INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    execution_time_ms INT,
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. PAYDAŞ İLETİŞİM BİLGİLERİ
CREATE TABLE IF NOT EXISTS stakeholders (
    stakeholder_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    organization VARCHAR(255),
    role VARCHAR(100),
    phone VARCHAR(50),
    category VARCHAR(50),
    notes TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME,
    is_active TINYINT(1) DEFAULT 1,
    INDEX idx_email (email),
    INDEX idx_org (organization)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. EMAIL GÖNDERME LOGLAR
CREATE TABLE IF NOT EXISTS email_logs (
    email_log_id INT AUTO_INCREMENT PRIMARY KEY,
    survey_id INT,
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(255),
    subject VARCHAR(255),
    sent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('sent', 'failed', 'bounced') DEFAULT 'sent',
    error_message TEXT,
    FOREIGN KEY (survey_id) REFERENCES surveys(survey_id) ON DELETE CASCADE,
    INDEX idx_survey (survey_id),
    INDEX idx_date (sent_date DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. VERİTABANI VERSİYONU
CREATE TABLE IF NOT EXISTS db_version (
    version VARCHAR(10) PRIMARY KEY,
    applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Versiyon kaydı
INSERT INTO db_version (version, description)
VALUES ('1.0', 'İlk kurulum - Anket sistemi temel tabloları (MySQL - Plesk Panel)')
ON DUPLICATE KEY UPDATE description = description;

-- ============================================================
-- KURULUM TAMAMLANDI!
-- 
-- Oluşturulan Tablolar:
--   1. surveys (Anketler)
--   2. survey_topics (Konular)
--   3. survey_responses (Yanıtlar)
--   4. api_logs (API Logları)
--   5. stakeholders (Paydaşlar)
--   6. email_logs (Email Logları)
--   7. db_version (Veritabanı Versiyonu)
-- 
-- Sonraki Adım: PHP dosyalarını yükleyin
-- ============================================================

