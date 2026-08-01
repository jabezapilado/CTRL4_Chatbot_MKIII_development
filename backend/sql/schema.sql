CREATE DATABASE IF NOT EXISTS soc_chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE soc_chatbot;

CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    student_number VARCHAR(20) NULL UNIQUE,
    staff_number VARCHAR(20) NULL UNIQUE,
    gender ENUM(
        'Male',
        'Female',
        'Prefer not to say',
        'Other'
    ) NULL,
    program VARCHAR(100) NULL,
    assigned_programs JSON NULL,
    office VARCHAR(255) NULL,
    support_statement TEXT NULL,
    consultation_rooms JSON NULL,
    consultation_schedules JSON NULL,
    role ENUM(
        'student',
        'staff',
        'admin'
    ) NOT NULL DEFAULT 'student',
    status ENUM(
        'active',
        'disabled'
    ) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL,
    INDEX idx_accounts_email (email),
    INDEX idx_accounts_role (role),
    INDEX idx_accounts_status (status)
);

CREATE TABLE IF NOT EXISTS inquiries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NULL,
    inquiry_type VARCHAR(100) NOT NULL,
    emotion_result VARCHAR(100) NOT NULL,
    escalated TINYINT(1) NOT NULL DEFAULT 0,
    appointment_recommended TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (account_id)
    REFERENCES accounts(id)
    ON DELETE SET NULL,
    INDEX idx_inquiries_account (account_id),
    INDEX idx_inquiries_created (created_at)
);

CREATE TABLE IF NOT EXISTS conversation_summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NULL,
    primary_concern VARCHAR(255) NOT NULL,
    conversation_type VARCHAR(100) NOT NULL,
    emotion_results VARCHAR(255) NOT NULL,
    flagged_status TINYINT(1) NOT NULL DEFAULT 0,
    appointment_recommendation VARCHAR(255) NOT NULL,
    recommendations TEXT NULL,
    suggested_intervention TEXT NULL,
    language_used VARCHAR(50) NOT NULL,
    total_messages INT NOT NULL,
    summary TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (account_id)
    REFERENCES accounts(id)
    ON DELETE SET NULL,
    INDEX idx_conversation_summaries_account (account_id),
    INDEX idx_conversation_summaries_flagged_status (flagged_status),
    INDEX idx_conversation_summaries_created (created_at)
);

CREATE TABLE IF NOT EXISTS escalations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NULL,
    summary_id INT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    intervention_notes TEXT NULL,
    created_at DATETIME NOT NULL,
    resolved_at DATETIME NULL,
    FOREIGN KEY (account_id)
    REFERENCES accounts(id)
    ON DELETE SET NULL,
    FOREIGN KEY (summary_id)
    REFERENCES conversation_summaries(id)
    ON DELETE SET NULL,
    INDEX idx_escalations_account (account_id),
    INDEX idx_escalations_summary (summary_id),
    INDEX idx_escalations_status (status)
);

CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    appointment_category VARCHAR(100) NOT NULL,
    appointment_mode VARCHAR(50) NOT NULL,
    preferred_date DATE NOT NULL,
    preferred_time_slot VARCHAR(20) NOT NULL,
    reason TEXT NOT NULL,
    status ENUM(
        'pending',
        'approved',
        'done',
        'did_not_attend',
        'cancelled'
    ) NOT NULL DEFAULT 'pending',
    counselor_notes TEXT NULL,
    appointment_source ENUM(
        'chatbot',
        'walk_in',
        'hotline',
        'messenger',
        'email',
        'staff_manual'
    ) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (account_id)
    REFERENCES accounts(id)
    ON DELETE RESTRICT,
    INDEX idx_appointments_account (account_id),
    INDEX idx_appointments_preferred_date (preferred_date),
    INDEX idx_appointments_status (status),
    INDEX idx_appointments_created (created_at)
);

CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    updated_at DATETIME NOT NULL
);

-- Never store plaintext passwords.
-- All passwords must be generated using Werkzeug's
-- generate_password_hash() before insertion.
-- Accounts can also be seeded through
-- backend/.env using scripts/setup_database.py.