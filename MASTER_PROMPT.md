# FIRSTSTEP CAREERS — MASTER PROMPT & DEVELOPMENT BLUEPRINT
## Complete Job Portal for Freshers Full-Stack Application

### Project Overview
**FirstStep Careers** is an enterprise-grade, full-stack recruitment portal specifically engineered to bridge recent graduates and entry-level talent with verified hiring companies and recruiters. The platform empowers freshers to discover entry-level opportunities, showcase their academic achievements and skills, and track application lifecycles. Recruiters can post vacancies, evaluate candidate resumes, and manage applicant progression, while administrators monitor platform safety, verify companies, and maintain job post integrity.

---

### Core Directives & Standards

1. **Full-Stack Implementation Architecture:**
   - **Backend:** Python Flask with modular blueprint architecture or unified clean service routing, robust session-based security, role-based authorization guards, form validation, and transactional database routines.
   - **Database:** Full MySQL integration with comprehensive relational schema (`schema.sql`), foreign keys with referential integrity, indexes, unique constraints (duplicate application and bookmark guards), and automated initialization/seeding.
   - **Frontend:** Semantic HTML5 templates (Jinja2 inheritance), modern CSS3 custom properties design system with high-contrast accessibility, and vanilla ES6+ JavaScript for reactive interactions (AJAX job filtering, modal dialogues, bookmark toggles, instant notifications).

2. **Visual & UX Polish:**
   - Premium SaaS recruitment aesthetics: Modern, clean, colorful, and engaging.
   - Deep Navy (`#172554`), Primary Royal Blue (`#3157D5`), Hover (`#233FA8`), Teal/Mint (`#0F9D91`), Warm Amber Accent (`#F5A524`), Surface White (`#FFFFFF`), Soft Tint Canvas (`#F5F7FC`).
   - Clean card-based responsive grids, micro-interactions, animated state transitions, badge systems for application statuses, and rich empty states.
   - Fully responsive across desktop (>1024px), tablet (641-1024px), and mobile (<=640px).

3. **Role-Based Workflows:**
   - **Fresher:** Registration, profile completion (education, degree, skills, graduation year, social links), secure resume upload (.pdf, .doc, .docx) with size/MIME verification, search and multi-criteria filtering, 1-click job application with duplicate prevention, saved jobs bookmarking, real-time application status tracker, and in-portal notifications.
   - **Recruiter:** Registration, company profile management with verification badge status, job creation/editing/closure, candidate pipeline review with resume viewer, status transition workflow (Under Review, Shortlisted, Interview Scheduled, Selected, Rejected) with candidate notes.
   - **Administrator:** Administrative command center with platform metrics, user management (activate/suspend), company verification, job moderation (publish/unpublish/delete), and dispute/report resolution.

4. **Security & Data Integrity:**
   - Password hashing with PBKDF2 / SHA256 / Werkzeug security.
   - Server-side role validation on every protected endpoint.
   - File upload sanitization: Secure filename hashing, extension verification, protected download routes preventing unauthorized resume scraping.
   - SQL injection prevention via parameterized queries and safe database drivers.
   - CSRF protection and form validation.

5. **Completeness & Zero-Simulation:**
   - No mock data or localStorage substitutes for primary data: Every user, profile, job, application, notification, and moderation action must persist to MySQL.
   - Complete set of working views, forms, modals, error pages (404, 403, 500), and seed data for immediate demonstration.

