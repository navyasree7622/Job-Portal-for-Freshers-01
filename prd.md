# Product Requirements Document (PRD)
## Job Portal for Freshers

**Document Version:** 1.0  
**Project Type:** Full-stack web application  
**Target Users:** Freshers, recruiters, and administrators  
**Recommended Technology Stack:** HTML, CSS, JavaScript, Python Flask, MySQL

---

## 1. Project Overview

The **Job Portal for Freshers** is a web-based platform designed to help recent graduates and entry-level job seekers discover suitable job opportunities and apply online. Recruiters can publish vacancies, review applications, and update candidate statuses. Administrators manage users, recruiters, job listings, and reports to maintain a trustworthy platform.

The system aims to make entry-level recruitment easier, more organized, and more accessible through a single application.

## 2. Problem Statement

Freshers may find it difficult to identify legitimate entry-level opportunities, understand eligibility requirements, and track applications submitted across different websites. Recruiters also need a convenient way to publish vacancies and manage applications from candidates.

This project provides a centralized platform where freshers can find and apply for jobs while recruiters manage vacancies and applications.

## 3. Project Objectives

- Provide a simple, responsive interface for freshers and recruiters.
- Allow users to register, log in, and access role-specific dashboards.
- Help freshers create profiles, add skills and education details, and upload resumes.
- Let freshers search and filter jobs and apply online.
- Enable recruiters to create, edit, publish, and close job listings.
- Allow recruiters to review applications and update their status.
- Provide an admin dashboard to oversee users, companies, job posts, and reports.
- Protect user information and validate uploaded files and form inputs.
- Make the application easy to maintain and extend in future versions.

## 4. Target Users and Roles

### 4.1 Fresher / Job Seeker
A student, recent graduate, or entry-level candidate looking for jobs or internships.

**Permissions:**
- Register and log in.
- Create and edit a profile.
- Add education, skills, location, and contact information.
- Upload or update a resume.
- Search, filter, view, and save jobs.
- Apply for eligible jobs.
- View submitted applications and their status.
- Receive in-portal notifications.

### 4.2 Recruiter
A company representative who publishes vacancies and reviews candidates.

**Permissions:**
- Register and log in as a recruiter.
- Create and manage a company profile.
- Create, edit, publish, and close job listings.
- View applications submitted to their own job listings.
- Review candidate profiles and resumes where permitted.
- Update application status, such as Under Review, Shortlisted, Interview, Selected, or Rejected.
- View basic application counts.

### 4.3 Administrator
A platform manager responsible for oversight and moderation.

**Permissions:**
- Access a protected admin dashboard.
- View and manage user and recruiter accounts.
- Review or verify company profiles.
- View, approve, reject, or remove suspicious job listings.
- Review user reports and complaints.
- Monitor platform activity and basic statistics.

Access must be enforced on the server, not only by hiding interface elements.

## 5. Scope

### 5.1 Minimum Viable Product (MVP)
The first release will include:
1. Home page with job search and featured/recent jobs.
2. Registration, login, logout, and role-based access.
3. Fresher profile and resume upload.
4. Recruiter company profile.
5. Job posting and job management.
6. Job search, filtering, and job details.
7. Online applications and duplicate-application prevention.
8. Application status tracking.
9. Admin user and job moderation.
10. Responsive layout, validation, testing, and deployment.

### 5.2 Future Enhancements
These features are optional and should be added after the MVP works:
- Email notifications.
- Skill-based job recommendations.
- Resume keyword matching.
- Interview scheduling and calendar integration.
- Job alerts and advanced saved-search options.
- Recruiter analytics and downloadable reports.
- Application feedback and candidate communication.
- Optional online aptitude tests.

### 5.3 Out of Scope for the First Release
- Guaranteed job placement.
- Payroll or employee management.
- Paid subscriptions or payment processing.
- Automated hiring decisions based solely on AI.
- Direct integration with external job boards unless separately approved.

## 6. User Workflow

### 6.1 Fresher Workflow
1. Visit the home page.
2. Register using the required details.
3. Log in securely.
4. Complete the profile with education, skills, location, and contact details.
5. Upload a resume.
6. Search jobs using keywords and filters.
7. Open a job to review responsibilities and eligibility.
8. Submit an application.
9. See a confirmation and the application in the dashboard.
10. Track status updates and notifications.

### 6.2 Recruiter Workflow
1. Register as a recruiter and log in.
2. Complete the company profile.
3. Create a job listing with required details.
4. Publish the job, subject to any admin approval rules.
5. Review applications for the recruiter's own jobs.
6. Open candidate profiles and permitted resume files.
7. Update candidate statuses.
8. Close the vacancy when recruitment ends.

### 6.3 Administrator Workflow
1. Log in through a protected admin account.
2. Review dashboard statistics.
3. Verify recruiter/company information as needed.
4. Review reported or pending job listings.
5. Approve, reject, or remove listings according to platform rules.
6. Manage accounts and investigate complaints.
7. Log out securely.

## 7. Functional Requirements

### FR-01: Registration
- The system shall allow users to register as a fresher or recruiter.
- Required fields shall be validated.
- The system shall reject duplicate email addresses.
- Passwords shall be stored using a secure password-hashing method, never as plain text.

### FR-02: Login and Logout
- The system shall authenticate registered users.
- The system shall provide role-specific access.
- Users shall be able to log out.
- Protected pages and API routes shall require valid authentication and authorization.

### FR-03: Fresher Profile
- Freshers shall be able to add and edit their name, contact details, location, education, skills, graduation year, and experience level.
- Users shall be able to upload and replace a resume.
- The system shall validate file type and size and store files safely.

### FR-04: Company Profile
- Recruiters shall be able to add and update company name, description, location, website, and contact details.
- The system shall support admin verification status.

### FR-05: Job Management
- Recruiters shall be able to create, edit, publish, and close their own job listings.
- Each job shall contain a title, description, responsibilities, required skills, eligibility, location, job type, experience level, and optional salary range and deadline.
- Closed or expired jobs shall not accept new applications.
- Recruiters shall not edit another recruiter's jobs.

### FR-06: Job Search and Filtering
- Visitors and logged-in users shall be able to browse published jobs.
- Users shall be able to search by keyword and filter by location, job type, skills, and experience level.
- The results shall show relevant job summaries and a link to the full details.

### FR-07: Job Application
- Logged-in freshers shall be able to apply for an open job.
- The system shall prevent a fresher from applying to the same job more than once.
- The system shall record the applicant, job, resume reference, application date, and current status.
- The system shall show a confirmation after a successful application.

### FR-08: Application Tracking
- Freshers shall be able to see their own applications and current statuses.
- Recruiters shall be able to see applications only for their own job listings.
- Recruiters shall be able to update application status.
- The system shall record status changes and display the latest status to the candidate.

### FR-09: Notifications
- The system shall create in-portal notifications for important application updates.
- Email notifications may be added as a later enhancement.

### FR-10: Admin Management
- Admins shall be able to view and manage accounts and job listings.
- Admin actions shall be restricted to authorized admin accounts.
- The system should retain a record of important moderation actions.

### FR-11: Saved Jobs
- Logged-in freshers shall be able to save and remove jobs from a saved-jobs list.
- Saved jobs shall be visible from the fresher dashboard.

### FR-12: Dashboard
- Fresher dashboard shall show profile completion, saved jobs, recent applications, and statuses.
- Recruiter dashboard shall show active jobs and application counts.
- Admin dashboard shall show counts of users, recruiters, jobs, and pending reports or reviews.

## 8. Non-Functional Requirements

### 8.1 Security
- Use password hashing and secure session management.
- Validate and sanitize all inputs on the server.
- Apply authorization checks to every protected action.
- Protect against common web vulnerabilities, including SQL injection, cross-site scripting, and cross-site request forgery where applicable.
- Restrict resume upload formats and sizes; use safe filenames and prevent executable uploads.
- Do not expose secrets, database credentials, or API keys in client-side code or public repositories.
- Use HTTPS in production.

### 8.2 Usability and Accessibility
- The interface shall be clear and beginner-friendly.
- Forms shall have labels, helpful validation messages, and clear success/error feedback.
- Navigation and key actions shall be consistent.
- Use readable typography, sufficient contrast, and keyboard-accessible controls.

### 8.3 Responsiveness
- Pages shall work on desktop, tablet, and mobile screen sizes.

### 8.4 Performance
- Common pages should load promptly under normal project-demo traffic.
- Search results should be paginated or limited where necessary.
- Database queries should use appropriate indexes as the dataset grows.

### 8.5 Reliability and Maintainability
- Keep frontend, backend, configuration, and database logic organized.
- Handle errors without exposing internal stack traces to users.
- Use environment variables for configuration.
- Provide setup instructions and a database schema or migration script.

## 9. Suggested Pages

### Public Pages
- Home
- Browse Jobs
- Job Details
- About
- Contact / Help
- Register
- Login

### Fresher Pages
- Fresher Dashboard
- My Profile
- Resume Management
- Saved Jobs
- My Applications
- Notifications

### Recruiter Pages
- Recruiter Dashboard
- Company Profile
- Post a Job
- Manage Jobs
- View Applicants
- Applicant Details

### Admin Pages
- Admin Dashboard
- Manage Users
- Manage Recruiters / Companies
- Manage Job Listings
- Reports and Complaints

## 10. Database Requirements

Suggested MySQL tables:

### `users`
- `id` (primary key)
- `name`
- `email` (unique)
- `password_hash`
- `role` (fresher, recruiter, admin)
- `is_active`
- `created_at`

### `fresher_profiles`
- `id` (primary key)
- `user_id` (foreign key to users)
- `phone`
- `location`
- `education`
- `graduation_year`
- `skills`
- `experience_level`
- `resume_path`
- `updated_at`

### `companies`
- `id` (primary key)
- `recruiter_user_id` (foreign key to users)
- `company_name`
- `description`
- `location`
- `website`
- `verification_status`
- `created_at`

### `jobs`
- `id` (primary key)
- `company_id` (foreign key to companies)
- `title`
- `description`
- `responsibilities`
- `required_skills`
- `eligibility`
- `location`
- `job_type`
- `experience_level`
- `salary_min` (optional)
- `salary_max` (optional)
- `application_deadline` (optional)
- `status` (draft, pending, published, closed, rejected)
- `created_at`

### `applications`
- `id` (primary key)
- `job_id` (foreign key to jobs)
- `fresher_user_id` (foreign key to users)
- `resume_path` or `resume_reference`
- `status`
- `applied_at`
- Unique constraint on (`job_id`, `fresher_user_id`) to prevent duplicate applications.

### `saved_jobs`
- `id` (primary key)
- `fresher_user_id` (foreign key to users)
- `job_id` (foreign key to jobs)
- `created_at`
- Unique constraint on (`fresher_user_id`, `job_id`).

### `notifications`
- `id` (primary key)
- `user_id` (foreign key to users)
- `message`
- `is_read`
- `created_at`

### `reports` (recommended)
- `id` (primary key)
- `reported_by_user_id`
- `job_id` (optional)
- `reason`
- `status`
- `created_at`

Use appropriate foreign keys, unique constraints, and indexes. The exact schema may be refined during implementation.

## 11. Recommended Technology Architecture

- **Frontend:** HTML5, CSS3, JavaScript.
- **Backend:** Python with Flask.
- **Database:** MySQL.
- **Database access:** Use parameterized queries or a suitable ORM.
- **Authentication:** Flask sessions with secure configuration and password hashing.
- **File uploads:** Store uploaded resumes in a controlled upload location or object storage; store only a safe reference/path and metadata in MySQL.
- **Deployment:** Host the Flask application and database on compatible services. Configure secrets through environment variables.

### High-Level Request Flow
1. User interacts with a page in the browser.
2. Frontend sends a request to the Flask backend.
3. Flask validates the request and checks the user's permissions.
4. Backend reads or writes data in MySQL.
5. Backend returns a response.
6. Frontend displays the result or error message.

## 12. Application Status Model

Suggested statuses:
- **Applied** — application submitted successfully.
- **Under Review** — recruiter is reviewing the application.
- **Shortlisted** — candidate has been shortlisted.
- **Interview Scheduled** — an interview has been arranged.
- **Selected** — candidate has been selected.
- **Rejected** — application was not successful.
- **Withdrawn** — candidate withdrew the application, if this option is implemented.

The system should validate allowed status transitions and record when a status is updated.

## 13. Acceptance Criteria

The MVP will be considered complete when:

1. A fresher can register, log in, complete a profile, and upload a valid resume.
2. A recruiter can register, create a company profile, and publish a job according to the configured approval rules.
3. Users can browse jobs and search/filter by supported fields.
4. A fresher can apply for an open job and cannot submit a duplicate application.
5. The fresher can view their application statuses.
6. A recruiter can view and manage applications only for their own jobs.
7. An admin can review users and job listings and take moderation actions.
8. Invalid input and unsupported uploads are rejected with clear messages.
9. Protected routes enforce role-based access on the backend.
10. The application works on desktop and mobile layouts.
11. The project includes setup instructions and database creation instructions.
12. The main user flows have been tested and no known critical defects remain.

## 14. Testing Plan

- **Registration tests:** valid registration, invalid fields, duplicate email.
- **Authentication tests:** correct/incorrect password, logout, role restrictions.
- **Profile tests:** save and edit profile, valid and invalid resume upload.
- **Job tests:** create, edit, close, search, filter, expired job behavior.
- **Application tests:** successful application, duplicate application, closed-job application, status updates.
- **Authorization tests:** candidate cannot manage jobs; recruiter cannot access another recruiter's applications; non-admin cannot access admin pages.
- **Responsive tests:** home, job details, login, dashboards, and forms on mobile and desktop.
- **Security tests:** input validation, safe file handling, secret configuration, and access control.

## 15. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Fake or misleading job posts | Recruiter verification, reporting, and admin moderation |
| Unauthorized access to candidate data | Server-side role checks and protected resume access |
| Unsafe resume uploads | File size/type validation, safe filenames, and controlled storage |
| Duplicate applications | Database unique constraint and backend validation |
| Lost credentials or exposed secrets | Password hashing and environment variables |
| Scope becoming too large | Complete and test MVP before optional features |

## 16. Deliverables

- Responsive frontend pages.
- Flask backend and application routes.
- MySQL schema / database setup script.
- Fresher, recruiter, and admin workflows.
- Resume upload and application tracking.
- Test cases and test results.
- `README.md` with installation, configuration, and run instructions.
- GitHub repository with secrets excluded.
- Deployment configuration and project demonstration.

## 17. Proposed Development Phases

1. Requirements confirmation and project setup.
2. UI design and responsive frontend.
3. MySQL schema and Flask configuration.
4. Authentication and role-based dashboards.
5. Fresher profile and resume upload.
6. Recruiter company profile and job management.
7. Job search, filtering, and application workflow.
8. Application tracking, notifications, and admin moderation.
9. Testing, security review, and bug fixing.
10. Deployment, documentation, and GitHub submission.

## 18. Success Metrics for the Project Demo

- All three roles can complete their intended workflows.
- A job can be posted and found through search.
- A fresher can apply and see the updated status.
- Recruiters cannot access applications belonging to other recruiters.
- Admin moderation works as expected.
- Core pages are usable on desktop and mobile.
- The setup guide allows another student or evaluator to run the project.

---

**End of PRD**

**Implementation note:** This PRD describes the intended product behavior. It does not mean the features have already been implemented. Confirm deployment provider, email service, and any optional features before development.
