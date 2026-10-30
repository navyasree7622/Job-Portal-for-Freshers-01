# Development Phases
## Job Portal for Freshers (FirstStep Careers)

**Project Type:** Full-stack Web Application  
**Technology Stack:** Python Flask, MySQL, HTML5, Modern CSS3, JavaScript (Vanilla ES6+)  
**Target Roles:** Freshers / Job Seekers, Recruiters / Employers, System Administrators  

---

### Phase 1: Requirements Confirmation, Project Setup & Environment Architecture
- Initialize directory structure adhering to production Flask conventions:
  - `database/` (MySQL schema scripts, initial migration/seed scripts)
  - `templates/` (Jinja2 templates with semantic HTML5, accessible structure)
  - `static/` (Custom CSS architecture, modular JavaScript, SVGs/icons)
  - `uploads/resumes/` (Secure file storage for applicant resumes)
- Set up configuration management (`config.py`, `.env.example`, `.env`) with secrets isolation.
- Configure MySQL connection handling with auto-reconnection and database initialization.

### Phase 2: Relational Database Schema & Models
- Implement normalized relational MySQL schema with primary keys, foreign keys, cascade rules, indexes, and unique constraints:
  - `users`: ID, name, email (unique), password_hash, role (`fresher`, `recruiter`, `admin`), is_active, created_at.
  - `fresher_profiles`: User ID, phone, location, education, graduation_year, skills, experience_level, bio, github_url, linkedin_url, resume_path, profile_completed_pct, updated_at.
  - `companies`: Recruiter user ID, company_name, description, industry, location, website, logo_path, verification_status (`pending`, `verified`, `rejected`), created_at.
  - `jobs`: Company ID, recruiter user ID, title, department/category, description, responsibilities, required_skills, eligibility, location, job_type (`Full-Time`, `Part-Time`, `Internship`, `Remote`), experience_level (`Fresher (0-1 yr)`, `0-2 yrs`), salary_min, salary_max, application_deadline, status (`draft`, `published`, `closed`), views_count, created_at.
  - `applications`: Job ID, fresher user ID, resume_path, cover_note, status (`Applied`, `Under Review`, `Shortlisted`, `Interview Scheduled`, `Selected`, `Rejected`, `Withdrawn`), recruiter_notes, applied_at, updated_at. Unique constraint on (`job_id`, `fresher_user_id`).
  - `saved_jobs`: Fresher user ID, job ID, created_at. Unique constraint on (`fresher_user_id`, `job_id`).
  - `notifications`: User ID, title, message, link, is_read, created_at.
  - `reports`: Reported by user ID, job ID, reason, details, status (`pending`, `reviewed`, `resolved`), created_at.
- Provide automated database table initialization and rich sample seed data for instant testing across all roles.

### Phase 3: Modern UI/UX Design System & Responsive Layouts
- Establish CSS custom properties design tokens based on design specification:
  - Deep Navy (`#172554`), Primary Royal Blue (`#3157D5`), Primary Hover (`#233FA8`), Teal/Mint (`#0F9D91`), Warm Amber Accent (`#F5A524`), Danger/Error (`#C23B4A`), Surface/Card (`#FFFFFF`), Canvas (`#F5F7FC`), Text Primary (`#172033`), Text Secondary (`#65718A`), Border (`#E1E7F0`).
- Modular CSS structure: `style.css` (variables, reset, typography, base layout), `components.css` (buttons, badges, cards, tables, forms, modals, toasts), `responsive.css` (breakpoints for desktop, tablet, and mobile).
- Semantic responsive master layout `templates/base.html` with role-aware navigation bar, mobile drawer, flash messages, user dropdown, and modern footer.

### Phase 4: Authentication, Authorization & Role-Based Access Control
- User registration with role selection (Fresher or Recruiter) and client/server validation.
- Secure password hashing using Werkzeug / bcrypt standards.
- Session-based login with remember-me capability, rate limiting consideration, and friendly error feedback.
- Strict server-side route protection decorators: `@login_required`, `@role_required('fresher')`, `@role_required('recruiter')`, `@role_required('admin')`.
- Safe logout and session invalidation.

### Phase 5: Fresher Module
- Fresher Dashboard:
  - Real-time profile completion progress calculation and visual progress bar.
  - Dynamic KPI metric counters: Total Applications, Shortlisted, Interviews Scheduled, Saved Jobs.
  - Recent application status tracker with timeline indicator.
  - Quick action links (Complete Profile, Upload Resume, Browse Matching Jobs).
- Comprehensive Fresher Profile:
  - Personal Information, Contact Info, Education, Degree, Branch, Graduation Year, Skills (with tags UI), Links (GitHub, LinkedIn, Portfolio).
  - Secure Resume Upload: Validate MIME type (.pdf, .doc, .docx), enforce file size limits (5MB max), sanitize filenames with UUID prefixes, protect resume access so only the owner and job recruiter can access it.
- Saved Jobs management: Bookmark jobs, view saved jobs list, remove bookmark, apply directly.

### Phase 6: Recruiter Module
- Recruiter Dashboard:
  - Metric counters: Active Job Postings, Total Received Applications, Shortlisted Candidates, Scheduled Interviews.
  - Recent job postings list with applicant counters and status badges.
  - Recent candidate applications stream with instant status action controls.
- Company Profile Management:
  - Edit company profile, industry, company description, official website, office location, contact details.
  - Display admin verification badge status (`Verified`, `Pending Review`).
- Job Management:
  - Post new job vacancies with title, department, job type, skills required, eligibility criteria, salary range, deadline, responsibilities, and status.
  - Edit existing job postings.
  - Close/Archive job postings (preventing further applications).
  - Strict ownership validation: Recruiters can only manage and view applications for their own postings.
- Applicant Review & Status Workflow:
  - Filter applicants by specific job posting and application status.
  - Candidate profile modal / detail view, including view/download resume.
  - Transition status (`Under Review`, `Shortlisted`, `Interview Scheduled`, `Selected`, `Rejected`) with recruiter feedback note.
  - Automatically generate applicant in-portal notification upon status update.

### Phase 7: Public Job Discovery, Advanced Search & Application Workflow
- Landing Page (Home):
  - Hero search panel with keyword, category, and location input.
  - Category quick-browse cards (Software Development, Data & AI, Cloud & DevOps, QA Testing, UI/UX Design, Core Engineering, Internships).
  - Featured & Recent Jobs grid.
  - "How It Works" step-by-step fresher onboarding guide.
  - Recruiter call-to-action banner.
- Browse / Search Jobs Page:
  - Live search filters: Keyword, Location, Job Type, Experience Level, Category, and Salary Range.
  - Reusable job cards with company info, badges, salary tags, deadline, and bookmark toggle.
  - Dynamic result counters and friendly empty state when no jobs match.
- Job Details Page:
  - Detailed company and role overview, eligibility checklist, responsibilities, required skills pills.
  - "Apply Now" interactive modal with resume preview/selection and optional cover note.
  - Real-time client & server validation:
    - Login prompt if unauthenticated.
    - Block non-freshers (e.g. recruiters) from applying.
    - Instant detection if already applied with badge "Already Applied".
    - Prevent application if job is closed or deadline passed.

### Phase 8: Notifications System & Candidate Application Tracker
- "My Applications" Candidate Tracker:
  - Filter by status, view submitted date, current status badge with color coding, recruiter response notes, and view original job post.
  - Option to withdraw pending applications.
- Real-time in-portal notifications:
  - Triggered on application submission, status updates by recruiters, and admin notices.
  - Notification drawer / page with "mark as read" and "clear all".

### Phase 9: Admin Dashboard & Platform Moderation
- Admin Overview Dashboard:
  - System-wide KPIs: Total registered users, total recruiters, verified companies, total jobs, total applications submitted.
  - Moderation queue: Pending company verifications, reported jobs, user accounts.
- Moderation Controls:
  - Manage Users: View, activate, deactivate/suspend accounts.
  - Manage Companies: Verify or reject recruiter company registrations.
  - Manage Jobs: Approve, unpublish, or delete fraudulent/spam job postings.
  - Reports & Grievances: Review candidate reports on suspicious job listings and resolve them.

### Phase 10: Quality Assurance, Automated Tests, Seed Data & Documentation
- End-to-end integration tests covering authentication, application submission, role authorization, and duplicate prevention.
- Production-grade error handling (custom 404, 403, 500 error pages with helpful links).
- Seed script to populate realistic data (Admin, Recruiters, Tech Companies, Jobs, Freshers, Applications, Notifications).
- Comprehensive `README.md` with step-by-step setup, MySQL configuration, testing instructions, and architecture breakdown.

