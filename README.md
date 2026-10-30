# FirstStep Careers — Job Portal for Freshers

A modern, full-stack recruitment platform engineered specifically for college freshers, recent graduates, and verified employers. Built with **Python Flask**, **MySQL**, **HTML5**, **Modern CSS3 Design System**, and **Vanilla JavaScript (ES6+)**.

---

## 🌟 Key Features

### 🎓 1. Fresher / Job Seeker
- **User Registration & Secure Login:** Role-based registration with email validation and Werkzeug password hashing.
- **Dynamic Profile Readiness:** Real-time profile completion score tracking education, degree, branch, passing year, CGPA, skills pills, and portfolio URLs.
- **Secure Resume Management:** Upload, replace, and view resumes with format validation (`.pdf`, `.doc`, `.docx`) and 5MB size limit. Protected resume URLs prevent public crawling.
- **Multi-Filter Job Discovery:** Instant search by keyword, skills, location, domain/category, employment type (Full-Time, Internship, Remote, Hybrid), and salary sorting.
- **1-Click Application:** Apply with existing profile resume or custom resume upload, optional cover notes, and database-level duplicate application prevention.
- **Candidate Application Tracker:** Visual progress stepper tracking lifecycle stages: `Applied` &rarr; `Under Review` &rarr; `Shortlisted` &rarr; `Interview Scheduled` &rarr; `Selected` / `Rejected`, with recruiter feedback notes and withdrawal options.
- **Saved Job Bookmarks:** Instant AJAX bookmark toggle for opportunities to review later.
- **In-Portal Notifications:** Real-time alerts for application status transitions and interview notices.

### 🏢 2. Hiring Recruiter
- **Recruiter Command Center:** KPI metrics (Active Jobs, Total Applicants, Shortlisted, Interviews Scheduled), recent job performance, and incoming candidate streams.
- **Company Profile Management:** Manage company branding, official website, headquarters location, industry, and track admin verification badge status.
- **Job Vacancy Lifecycle:** Post new entry-level jobs with salary ranges, required skill tags, eligibility criteria, and deadlines. Easily edit, close, or re-open listings.
- **Applicant Pipeline & Evaluation:** Filter applicants by specific job openings and status. Access candidate education summaries and download encrypted resumes.
- **Candidate Status Workflow:** Move candidates across stages (`Under Review`, `Shortlisted`, `Interview Scheduled`, `Selected`, `Rejected`) with personalized recruiter notes that automatically notify the applicant.
- **Strict Data Isolation:** Recruiters can only access and manage applications submitted to their own job postings.

### 🛡️ 3. Platform Administrator
- **Admin Command Center:** System-wide metrics (Total Users, Freshers, Recruiters, Total Jobs, Submitted Applications, Safety Reports).
- **User Account Moderation:** Audit registered users, filter by role, and activate or suspend accounts.
- **Company Verification:** Verify legitimate employer domains or reject unverified accounts to protect freshers.
- **Job Moderation:** Inspect platform vacancies, close, re-publish, or delete fraudulent listings.
- **Reports & Grievances:** Review candidate reports on suspicious listings or fee requests, and mark them as resolved or dismissed.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
|---|---|
| **Backend** | Python 3.10+, Flask 3.1, Werkzeug (Password Hashing & Security) |
| **Database** | MySQL / MariaDB (Relational schema with Foreign Keys, Cascades & Unique Constraints) |
| **Database Driver** | PyMySQL 1.2+ with Dictionary Cursors and Transactional Integrity |
| **Frontend** | HTML5, CSS3 Custom Properties (Design Tokens), Vanilla ES6+ JavaScript |
| **UI Aesthetics** | Deep Navy (`#172554`), Royal Blue (`#3157D5`), Mint Teal (`#0F9D91`), Warm Amber (`#F5A524`) |
| **Testing** | Python `unittest` integration & unit test suite (13 comprehensive test cases) |

---

## 🗄️ Database Schema (`job_portal_db`)

The database architecture consists of 8 fully-normalized relational tables:

1. `users` — Authentication credentials, role (`fresher`, `recruiter`, `admin`), active status.
2. `fresher_profiles` — Academic degrees, college, graduation year, CGPA, technical skills, bio, URLs, resume references.
3. `companies` — Organization name, industry, headquarters, website, contact email, verification status (`verified`, `pending`, `rejected`).
4. `jobs` — Title, category, job type, location, experience bracket, salary range, deadlines, description, required skills, eligibility, status (`published`, `closed`, `draft`), view counters.
5. `applications` — Job ID, Fresher User ID, resume reference, cover note, status lifecycle, recruiter notes. Enforces a `UNIQUE(job_id, fresher_user_id)` constraint to prevent duplicate applications.
6. `saved_jobs` — Bookmarked job listings per candidate with `UNIQUE(fresher_user_id, job_id)` constraint.
7. `notifications` — In-portal candidate and recruiter activity notifications with unread badge tracking.
8. `reports` — Candidate reports on suspicious or misleading job listings for admin moderation.

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10+ installed
- MySQL Server (e.g. via XAMPP or standalone MySQL Server) running on port 3306

### 2. Configure Environment (`.env`)
Create or edit `.env` in the project root:
```env
SECRET_KEY=firststep_secret_key_production_grade_super_secret_2026
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=job_portal_db
MYSQL_PORT=3306
```

### 3. Initialize & Seed Database
Ensure MySQL is running, then initialize schema and sample seed data:
```bash
# Run schema and seed script
python database/seed_data.py
```
*(This automatically creates the database if not present, builds all tables, and seeds realistic test data).*

### 4. Run the Flask Web Application
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Credentials

For quick evaluation, pre-configured test accounts are ready:

| Role | Email | Password | Details |
|---|---|---|---|
| **Fresher** | `rahul.sharma@gmail.com` | `fresher123` | B.Tech CSE (2026), Active applications & bookmarks |
| **Fresher** | `ananya.patel@gmail.com` | `fresher123` | BCA graduate, Java / Full-Stack profile |
| **Recruiter** | `tcs.careers@tcs.com` | `recruiter123` | TCS (Verified Employer), Active job listings & applicants |
| **Recruiter** | `careers@infosys.com` | `recruiter123` | Infosys Technologies (Verified Employer) |
| **Admin** | `admin@firststep.com` | `admin123` | System Administrator with full moderation privileges |

*(The Sign-In page also includes 1-click credential auto-fill buttons for immediate testing).*

---

## 🧪 Running Automated Tests

Run the complete test suite covering authentication, role-based authorization, job filtering, application submission, duplicate prevention, and secure file downloads:
```bash
python -m unittest tests/test_app.py
```

---

## 📁 Project Directory Structure

```text
Job_Portal_for_Freshers/
├── app.py                     # Main Flask application & route controllers
├── config.py                  # Configuration loader & constants
├── requirements.txt           # Python dependency requirements
├── .env                       # Local environment secrets & DB credentials
├── .env.example               # Template environment configuration
├── README.md                  # Comprehensive project documentation
├── prd.md                     # Product Requirements Document
├── design.md                  # UI/UX & Architecture Design Document
├── phases.md                  # 10-Phase Development Roadmap
├── MASTER_PROMPT.md           # Master Development Blueprint
├── database/
│   ├── schema.sql             # Relational MySQL schema DDL
│   ├── seed_data.py           # Database seeder with realistic test data
│   └── db.py                  # Database connection & query helper functions
├── templates/
│   ├── base.html              # Responsive base layout with role-aware nav
│   ├── index.html             # Landing page with hero search & category cards
│   ├── login.html             # Sign in with 1-click test credentials
│   ├── register.html          # Registration with Fresher / Recruiter selection
│   ├── jobs.html              # Job discovery with live multi-filter sidebar
│   ├── job_details.html       # Job description, requirements & apply modal
│   ├── about.html             # Mission & platform pillars
│   ├── contact.html           # Support form & FAQ accordion
│   ├── fresher_dashboard.html # Fresher metrics, profile readiness & trackers
│   ├── profile.html           # Full profile & resume management
│   ├── applications.html      # Candidate application progress stepper
│   ├── saved_jobs.html        # Bookmarked jobs grid
│   ├── notifications.html     # In-portal notification center
│   ├── recruiter_dashboard.html # Recruiter KPIs, active jobs & applicant queue
│   ├── company_profile.html   # Organization profile & verification status
│   ├── post_job.html          # Job posting & vacancy editing form
│   ├── manage_jobs.html       # Recruiter vacancy management table
│   ├── applicants.html        # Candidate pipeline review & status updater
│   ├── admin_dashboard.html   # Admin oversight & system statistics
│   ├── admin_users.html       # User account moderation
│   ├── admin_companies.html   # Recruiter company verification
│   ├── admin_jobs.html        # Platform job moderation
│   ├── admin_reports.html     # Candidate safety reports & complaints
│   ├── 404.html               # Not Found error page
│   ├── 403.html               # Access Forbidden error page
│   └── 500.html               # Internal Server Error page
├── static/
│   ├── css/
│   │   ├── style.css          # Design tokens, typography, hero & job cards
│   │   ├── components.css     # Buttons, forms, badges, modals, steppers
│   │   └── responsive.css     # Mobile drawer & adaptive breakpoints
│   └── js/
│       ├── main.js            # Mobile toggle, dropdowns, bookmarks, toasts
│       ├── jobs.js            # Debounced search & filter handler
│       └── forms.js           # Password reveal, file validation & score calculator
├── tests/
│   └── test_app.py            # Automated unit & integration test suite
└── uploads/
    └── resumes/               # Protected candidate resume storage
```

