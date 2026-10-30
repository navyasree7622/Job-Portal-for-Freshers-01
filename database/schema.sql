-- ==========================================================
-- FirstStep Careers - Job Portal for Freshers
-- Database Schema (MySQL / MariaDB)
-- ==========================================================

CREATE DATABASE IF NOT EXISTS `job_portal_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `job_portal_db`;

-- Drop tables in reverse dependency order if resetting
DROP TABLE IF EXISTS `audit_logs`;
DROP TABLE IF EXISTS `reports`;
DROP TABLE IF EXISTS `notifications`;
DROP TABLE IF EXISTS `saved_jobs`;
DROP TABLE IF EXISTS `applications`;
DROP TABLE IF EXISTS `jobs`;
DROP TABLE IF EXISTS `companies`;
DROP TABLE IF EXISTS `fresher_profiles`;
DROP TABLE IF EXISTS `users`;

-- 1. Users Table
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('fresher', 'recruiter', 'admin') NOT NULL DEFAULT 'fresher',
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_users_email` (`email`),
    INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Fresher Profiles Table
CREATE TABLE `fresher_profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `phone` VARCHAR(20) DEFAULT NULL,
    `location` VARCHAR(120) DEFAULT NULL,
    `education` VARCHAR(100) DEFAULT NULL,
    `degree` VARCHAR(120) DEFAULT NULL,
    `institution` VARCHAR(200) DEFAULT NULL,
    `graduation_year` INT DEFAULT NULL,
    `cgpa` VARCHAR(20) DEFAULT NULL,
    `skills` TEXT DEFAULT NULL,
    `experience_level` VARCHAR(50) DEFAULT 'Fresher (0-1 yr)',
    `bio` TEXT DEFAULT NULL,
    `github_url` VARCHAR(255) DEFAULT NULL,
    `linkedin_url` VARCHAR(255) DEFAULT NULL,
    `portfolio_url` VARCHAR(255) DEFAULT NULL,
    `resume_path` VARCHAR(255) DEFAULT NULL,
    `resume_filename` VARCHAR(255) DEFAULT NULL,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_fresher_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Companies Table
CREATE TABLE `companies` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `recruiter_user_id` INT NOT NULL UNIQUE,
    `company_name` VARCHAR(150) NOT NULL,
    `industry` VARCHAR(100) DEFAULT 'Information Technology',
    `description` TEXT DEFAULT NULL,
    `location` VARCHAR(150) DEFAULT NULL,
    `website` VARCHAR(255) DEFAULT NULL,
    `contact_email` VARCHAR(150) DEFAULT NULL,
    `verification_status` ENUM('pending', 'verified', 'rejected') DEFAULT 'pending',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_company_recruiter` FOREIGN KEY (`recruiter_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Jobs Table
CREATE TABLE `jobs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `company_id` INT NOT NULL,
    `recruiter_user_id` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `category` VARCHAR(100) NOT NULL DEFAULT 'Software Development',
    `description` TEXT NOT NULL,
    `responsibilities` TEXT DEFAULT NULL,
    `required_skills` TEXT NOT NULL,
    `eligibility` TEXT DEFAULT NULL,
    `location` VARCHAR(120) NOT NULL,
    `job_type` ENUM('Full-Time', 'Part-Time', 'Internship', 'Remote', 'Hybrid') NOT NULL DEFAULT 'Full-Time',
    `work_arrangement` ENUM('Onsite', 'Remote', 'Hybrid') NOT NULL DEFAULT 'Onsite',
    `experience_level` VARCHAR(50) NOT NULL DEFAULT 'Fresher (0-1 yr)',
    `salary_min` INT DEFAULT NULL,
    `salary_max` INT DEFAULT NULL,
    `application_deadline` DATE DEFAULT NULL,
    `status` ENUM('draft', 'published', 'closed') NOT NULL DEFAULT 'published',
    `is_featured` TINYINT(1) NOT NULL DEFAULT 0,
    `is_sample` TINYINT(1) NOT NULL DEFAULT 1,
    `views_count` INT NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_job_company` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_job_recruiter` FOREIGN KEY (`recruiter_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    INDEX `idx_jobs_category` (`category`),
    INDEX `idx_jobs_location` (`location`),
    INDEX `idx_jobs_job_type` (`job_type`),
    INDEX `idx_jobs_work_arrangement` (`work_arrangement`),
    INDEX `idx_jobs_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Applications Table
CREATE TABLE `applications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `job_id` INT NOT NULL,
    `fresher_user_id` INT NOT NULL,
    `resume_path` VARCHAR(255) NOT NULL,
    `cover_note` TEXT DEFAULT NULL,
    `status` ENUM('Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected', 'Withdrawn') NOT NULL DEFAULT 'Applied',
    `recruiter_notes` TEXT DEFAULT NULL,
    `applied_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_app_job` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_app_fresher` FOREIGN KEY (`fresher_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `uq_job_fresher` UNIQUE (`job_id`, `fresher_user_id`),
    INDEX `idx_app_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Saved Jobs Table
CREATE TABLE `saved_jobs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `fresher_user_id` INT NOT NULL,
    `job_id` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_saved_fresher` FOREIGN KEY (`fresher_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_saved_job` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE CASCADE,
    CONSTRAINT `uq_saved_fresher_job` UNIQUE (`fresher_user_id`, `job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Notifications Table
CREATE TABLE `notifications` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(150) NOT NULL,
    `message` TEXT NOT NULL,
    `link` VARCHAR(255) DEFAULT NULL,
    `is_read` TINYINT(1) NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_notif_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    INDEX `idx_notif_user_read` (`user_id`, `is_read`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Reports Table
CREATE TABLE `reports` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `reported_by_user_id` INT NOT NULL,
    `job_id` INT NOT NULL,
    `reason` VARCHAR(100) NOT NULL,
    `details` TEXT DEFAULT NULL,
    `status` ENUM('pending', 'reviewed', 'resolved', 'dismissed') NOT NULL DEFAULT 'pending',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_report_user` FOREIGN KEY (`reported_by_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_report_job` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`id`) ON DELETE CASCADE,
    INDEX `idx_report_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Audit Logs Table
CREATE TABLE `audit_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NULL,
    `action` VARCHAR(150) NOT NULL,
    `details` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_audit_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_audit_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
