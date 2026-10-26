-- ============================================================
-- AI-BASED STUDENT PERFORMANCE PREDICTION & PERSONALIZED LEARNING
-- Complete MySQL Relational Database Schema
-- Database: student_performance_db
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_performance_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE student_performance_db;

-- ------------------------------------------------------------
-- 1. USERS TABLE (Authentication & Role Based Access)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'teacher', 'admin') NOT NULL DEFAULT 'student',
    token VARCHAR(128) UNIQUE NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. TEACHERS TABLE (Teacher Profiles)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_code VARCHAR(20) NOT NULL UNIQUE,
    user_id INT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    subject VARCHAR(100) NOT NULL,
    classes_count INT NOT NULL DEFAULT 1,
    status ENUM('Active', 'On Leave', 'Inactive') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. SUBJECTS TABLE (Academic Subjects)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    teacher_name VARCHAR(100) NOT NULL,
    teacher_id INT NULL,
    credits INT NOT NULL DEFAULT 3,
    students_count INT NOT NULL DEFAULT 0,
    color VARCHAR(20) DEFAULT '#2c7be5',
    progress INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. STUDENTS TABLE (Student Profiles & Summaries)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_code VARCHAR(20) NOT NULL UNIQUE,
    user_id INT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    grade_class VARCHAR(20) NOT NULL DEFAULT '10-A',
    level ENUM('Needs Improvement', 'Average', 'Good', 'Excellent') NOT NULL DEFAULT 'Average',
    attendance_pct INT NOT NULL DEFAULT 85,
    avg_grade DECIMAL(4, 1) NOT NULL DEFAULT 12.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_student_level (level)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 5. PREDICTIONS TABLE (AI Predicted Grades & Recommendations)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NULL,
    student_email VARCHAR(120) NULL,
    predicted_grade DECIMAL(4, 1) NOT NULL,
    performance_level VARCHAR(50) NOT NULL,
    recommendations JSON NOT NULL,
    student_data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL,
    INDEX idx_pred_created (created_at),
    INDEX idx_pred_level (performance_level)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 6. STUDENT_STUDY_HABITS TABLE (Personalized Habits)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS student_study_habits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_email VARCHAR(120) NOT NULL UNIQUE,
    hours_per_day DECIMAL(3, 1) DEFAULT 2.0,
    focus_subject VARCHAR(100) DEFAULT 'Mathematics',
    revision_days INT DEFAULT 3,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 7. ATTENDANCE_RECORDS TABLE (Daily Attendance Tracker)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_date DATE NOT NULL,
    student_code VARCHAR(20) NOT NULL,
    is_present BOOLEAN NOT NULL DEFAULT TRUE,
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date_student (record_date, student_code)
) ENGINE=InnoDB;
