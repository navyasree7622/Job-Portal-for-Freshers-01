# Design Document
## Job Portal for Freshers

**Document Version:** 1.0  
**Project Type:** Full-stack web application  
**Design Goal:** A polished, modern, colorful, responsive, and easy-to-use job portal for fresh graduates.

---

## 1. Design Vision

Create a professional job-search platform that feels trustworthy, welcoming, and simple for first-time job seekers. The website should look like a real recruitment product rather than a basic college assignment.

The visual design should use a consistent design system, clear typography, well-spaced layouts, meaningful icons, accessible contrast, helpful empty states, and responsive components.

### Design Principles
- **Professional:** Clean layouts, consistent spacing, and restrained use of color.
- **Fresher-friendly:** Clear wording and guidance for users who are applying for their first job.
- **Easy to navigate:** Main actions such as Search Jobs, Apply, Post a Job, and Track Applications should be easy to find.
- **Responsive:** Support desktop, tablet, and mobile.
- **Accessible:** Use semantic HTML, visible focus states, keyboard-friendly navigation, and readable contrast.
- **Consistent:** Reuse shared components, typography, colors, buttons, cards, and form styles.
- **Functional:** Every visible button, link, filter, and form must perform the action it promises.

## 2. Brand and Visual Identity

### Working Product Name
**FirstStep Careers** — a suggested name for the portal. Keep the name easy to change from a single shared location if a different name is chosen.

### Tagline
**Your first step toward your future.**

### Visual Style
Use a modern SaaS-style recruitment interface with:
- A deep navy or indigo base for trust.
- Bright blue for primary actions and links.
- Teal or mint accents for success states and positive progress.
- Warm amber for highlights and reminders.
- Soft tinted page backgrounds and white cards.
- Subtle shadows, fine borders, rounded corners, and restrained gradients.

Avoid a completely white, plain, or unfinished appearance. Do not use too many unrelated colors, excessive gradients, distracting animations, or oversized decorations.

## 3. Color System

Use CSS custom properties so colors can be updated centrally.

| Token | Suggested value | Use |
|---|---|---|
| Primary | `#3157D5` | Primary buttons, links, selected controls |
| Primary Dark | `#233FA8` | Hover and active states |
| Navy | `#172554` | Main headings, navigation, footer |
| Secondary | `#0F9D91` | Positive accents and progress |
| Accent | `#F5A524` | Highlights, tips, and badges |
| Page Background | `#F5F7FC` | Main application background |
| Surface | `#FFFFFF` | Cards, forms, menus |
| Text Primary | `#172033` | Main content |
| Text Secondary | `#65718A` | Supporting text |
| Border | `#E1E7F0` | Dividers, input outlines |
| Success | `#16845B` | Success states |
| Warning | `#A86508` | Warning states |
| Danger | `#C23B4A` | Errors and destructive actions |
| Info | `#2674C8` | Informational messages |

Check contrast before finalizing text and background combinations. Do not communicate status through color alone; also use labels and icons.

## 4. Typography

Use **Inter** or a similar clean sans-serif font. If an external font cannot load, use a system sans-serif fallback.

Suggested scale:
- Page title: 30–36 px desktop, 26–30 px mobile.
- Section heading: 22–26 px.
- Card heading: 16–20 px.
- Body text: 14–16 px.
- Supporting text: 12–14 px.
- Button text: 14–16 px, medium or semibold.

Use consistent font weights and line heights. Avoid long paragraphs in dashboard cards.

## 5. Layout and Spacing

- Use a centered content container with a maximum width around 1200–1280 px.
- Use a consistent spacing scale based on 4 px or 8 px increments.
- Use rounded cards with approximately 12–18 px corner radii.
- Keep sufficient space between page sections and form fields.
- Use a responsive grid for job cards and dashboard metrics.
- Use a sticky top navigation only when it improves navigation and does not cover content.
- On mobile, collapse navigation into an accessible menu and stack multi-column layouts.

### Responsive Breakpoints
Use sensible CSS breakpoints, for example:
- Mobile: up to 640 px.
- Tablet: 641–1024 px.
- Desktop: above 1024 px.

These are design guidelines, not rigid constraints. Ensure the actual content fits each viewport.

## 6. Navigation Structure

### Public Navigation
- Logo / FirstStep Careers
- Home
- Find Jobs
- Career Tips (optional informational page)
- About
- Login
- **Get Started** primary button

### Fresher Navigation
- Dashboard
- Find Jobs
- Saved Jobs
- My Applications
- My Profile
- Notifications
- Account menu / Logout

### Recruiter Navigation
- Dashboard
- Manage Jobs
- Post a Job
- Applicants
- Company Profile
- Notifications
- Account menu / Logout

### Admin Navigation
- Overview
- Users
- Recruiters / Companies
- Job Listings
- Reports
- Settings (only if implemented)
- Logout

Show only the navigation items appropriate to the signed-in user's role. The backend must also enforce permissions.

## 7. Page Designs

### 7.1 Home Page

**Purpose:** Explain the portal quickly and lead users toward job discovery or registration.

**Layout:**
1. Responsive top navigation.
2. Hero section with a strong headline, short supporting text, and a job-search panel.
3. Search inputs for keyword/job title and location, plus a Search Jobs button.
4. Small trust or benefit highlights, without unsupported statistics.
5. Browse-by-category section, such as Software Development, Data & Analytics, Design, Marketing, Business, and Internships.
6. Latest jobs section using reusable job cards.
7. “How it works” section: Create Profile → Find Jobs → Apply → Track Progress.
8. Call-to-action section for freshers and recruiters.
9. Footer with About, Help/Contact, Privacy, and Terms links where implemented.

**Design notes:**
- Use a subtle blue-to-indigo background treatment or a soft tinted hero panel.
- Keep the search form visually prominent.
- Use original illustrations or simple icons only when they improve clarity.
- Do not invent partner logos, user counts, placement statistics, or testimonials.

### 7.2 Register Page

**Layout:**
- Brand logo and concise welcome heading.
- Role selection: Fresher or Recruiter.
- Name, email, password, and confirm password fields as required.
- Clear password requirements and inline validation.
- Terms/privacy acknowledgment if these pages are provided.
- Primary Create Account button.
- Link to Login.

**Behavior:**
- Show validation errors next to relevant fields.
- Disable repeated submission while a request is processing.
- Show a clear success or failure message.
- Do not display raw server errors or reveal whether sensitive account details exist unnecessarily.

### 7.3 Login Page

**Layout:**
- Focused sign-in card with a small brand area.
- Email and password fields.
- Show/hide password control.
- Remember-me option only if securely implemented.
- Forgot Password link only if password recovery is implemented.
- Login button and registration link.

**Behavior:**
- Display a helpful generic error for invalid credentials.
- Route authenticated users to the correct dashboard.
- Protect all private pages on the server.

### 7.4 Job Search Page

**Layout:**
- Page title and result count.
- Search bar with keyword and location.
- Filter panel for job type, experience level, skills, and location.
- Sort control where supported.
- Job cards in a two-column layout on wide screens, one column on mobile.
- Pagination or Load More behavior for larger result sets.

**Job Card Content:**
- Job title.
- Company name and location.
- Job type and entry-level label.
- Short description or skill tags.
- Salary range only when supplied by the recruiter.
- Posted date and application deadline when available.
- View Details action and Save Job control.

**States:**
- Loading skeleton.
- No results with suggestions to adjust filters.
- Error message with a retry action.
- Empty saved-jobs state.

### 7.5 Job Details Page

Display:
- Job title and company information.
- Location, job type, experience level, and salary if supplied.
- Overview, responsibilities, required skills, and eligibility.
- Application deadline and posting date when available.
- Apply Now button.
- Save Job control.
- Report Job action if reporting is implemented.

The Apply Now button should clearly indicate if login is required, the application was already submitted, or the job is closed.

### 7.6 Fresher Dashboard

**Visual layout:**
- Greeting and short next-step message.
- Profile completion card with a progress indicator based on actual saved profile fields.
- Metric cards: Applications, Interviews, Shortlisted, Saved Jobs.
- Recent applications table or cards with job, company, date, and status.
- Recommended or latest jobs section.
- Quick actions: Complete Profile, Upload Resume, Find Jobs.

Only show accurate values derived from the database. Do not hardcode dashboard counts.

### 7.7 Fresher Profile and Resume

Use clear sections or tabs:
- Personal Information
- Education
- Skills
- Experience / Projects
- Resume

Design requirements:
- Labels remain visible above inputs.
- Show required and optional fields clearly.
- Provide Save Changes and Cancel actions.
- Show the current resume filename and upload date when available.
- Display file format and size limits before upload.
- Provide upload progress if feasible.
- Never expose a private resume through a guessable public URL.

### 7.8 Saved Jobs Page

- Display saved jobs using the shared job-card component.
- Allow removing a saved job.
- Show whether the vacancy is still open.
- Provide a useful empty state with a Find Jobs action.

### 7.9 My Applications Page

Use a responsive table on desktop and stacked application cards on mobile.

Fields:
- Job title.
- Company.
- Applied date.
- Current status.
- View Job / View Details action.

Use consistent status badges with both text and distinct visual treatment:
- Applied
- Under Review
- Shortlisted
- Interview Scheduled
- Selected
- Rejected
- Withdrawn, if supported

### 7.10 Recruiter Dashboard

- Welcome section and Post a Job primary action.
- Metric cards for active jobs, total applications, shortlisted candidates, and interviews.
- Recent job listings with status and application count.
- Recent applications with candidate name, job title, and status.
- Helpful empty state when the recruiter has not posted a job.

### 7.11 Post / Edit Job Page

Organize the form into clear sections:
1. Basic Information: job title, department/category, job type.
2. Job Details: description and responsibilities.
3. Requirements: education, skills, and experience level.
4. Location and Compensation: location and optional salary range.
5. Application Details: deadline and vacancy status.

Provide Save Draft if supported, Preview, and Publish Job actions. Clearly mark optional fields. Validate deadlines and salary ranges on the backend as well as the frontend.

### 7.12 Applicants Page

- Filter applicants by job and status.
- Show candidate name, education/skills summary, application date, and status.
- Allow authorized recruiters to open a candidate's permitted profile/resume.
- Provide status actions with confirmation where appropriate.
- Show empty, loading, and error states.
- Never allow recruiters to view applications for jobs owned by another recruiter.

### 7.13 Admin Dashboard

- Overview metric cards for users, recruiters, published jobs, pending reviews, and reports.
- Tables with search, filters, and pagination.
- Actions to review, approve, reject, suspend, or remove records as authorized.
- Confirmation dialogs for destructive actions.
- Clear audit information for important moderation actions where implemented.

### 7.14 About, Help, and Footer

Provide concise project information and working contact/help options. Do not show fake contact information or non-functional links. Privacy and Terms links must lead to actual content before being presented as available policies.

## 8. Shared UI Components

Build reusable components and keep their visual behavior consistent:
- Header and role-aware navigation.
- Footer.
- Primary, secondary, outline, and danger buttons.
- Form inputs, selects, textareas, checkboxes, and validation messages.
- Job card and job status badge.
- Company summary.
- Dashboard metric card.
- Data table and mobile card list.
- Search and filter panel.
- Modal / confirmation dialog.
- Toast or inline notification.
- Loading skeleton.
- Empty state.
- Pagination.
- File upload control.
- Profile completion indicator.

Each component should have consistent spacing, typography, focus styles, hover states, disabled states, and error states.

## 9. Interaction and Feedback Rules

Every interactive element must work.

- Buttons must perform the action stated in their labels.
- Navigation links must lead to valid pages.
- Search and filters must affect the actual displayed results.
- Forms must validate input and submit to the backend.
- Loading states must appear during requests where appropriate.
- Success and error messages must be clear and accessible.
- Destructive actions should require confirmation.
- Prevent duplicate submissions while requests are processing.
- Do not use placeholder alerts as a substitute for real functionality.
- Do not show success messages when the backend operation fails.

## 10. Accessibility Requirements

- Use semantic HTML elements and correct heading order.
- Provide accessible labels for all form fields.
- Ensure all controls can be reached and operated with a keyboard.
- Provide visible keyboard focus indicators.
- Use adequate color contrast.
- Do not rely on color alone to communicate application status.
- Provide meaningful alternative text for informative images.
- Use accessible names for icon-only controls.
- Respect reduced-motion preferences.
- Announce important form errors and status updates accessibly.

## 11. Motion and Visual Effects

Use restrained effects only:
- Short hover transitions for buttons and cards.
- Subtle entrance transitions when they support comprehension.
- Small animated loading indicators.
- Gentle focus and selected-state transitions.

Avoid excessive parallax, constant motion, distracting background animations, or effects that slow down the site. Ensure the interface remains usable when reduced motion is enabled.

## 12. Responsive Behavior

### Desktop
- Full navigation.
- Wide search panel.
- Multi-column job listings and metric cards.
- Tables for application management.

### Tablet
- Compact navigation.
- Two-column grids where space allows.
- Filter panel may become collapsible.

### Mobile
- Compact header and menu.
- Single-column content.
- Full-width primary actions when useful.
- Filter controls in a drawer or collapsible panel.
- Tables converted to cards or horizontally scrollable only when necessary.
- No unintended horizontal page overflow.
- Inputs and buttons large enough for touch interaction.

## 13. Frontend and Backend Design Boundaries

The frontend is responsible for presentation, client-side convenience validation, and sending requests. The Flask backend is responsible for authentication, authorization, authoritative validation, business rules, and database access.

The UI must not be treated as a security boundary. Role checks, ownership checks, duplicate-application prevention, and job status checks must be enforced on the backend and, where appropriate, by database constraints.

### Design-to-Implementation Request Flow
1. User interacts with a page.
2. Frontend submits a request to Flask.
3. Flask authenticates the user and checks permissions.
4. Flask validates input and applies business rules.
5. Flask reads or updates MySQL.
6. Flask returns a success or error response.
7. Frontend updates the screen based on the actual response.

## 14. Suggested Frontend Organization

Adapt this structure to the chosen implementation approach, but keep responsibilities clear:

```text
Job_Portal_for_Freshers/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── database/
│   └── schema.sql
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── jobs.html
│   ├── job_details.html
│   ├── fresher_dashboard.html
│   ├── profile.html
│   ├── applications.html
│   ├── recruiter_dashboard.html
│   ├── post_job.html
│   ├── applicants.html
│   └── admin_dashboard.html
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── components.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── main.js
│   │   ├── jobs.js
│   │   └── forms.js
│   └── images/
└── uploads/
    └── .gitkeep
```

This is a suggested structure. If the project uses Flask blueprints or a separate frontend, organize the files accordingly without losing the shared design system.

## 15. Design Acceptance Checklist

- [ ] The home page looks polished and communicates the purpose immediately.
- [ ] The design uses a consistent color palette and typography.
- [ ] Login and registration pages are clear and responsive.
- [ ] Job cards are readable and display useful job information.
- [ ] Fresher, recruiter, and admin dashboards are visually distinct but consistent.
- [ ] Forms include labels, validation, loading, success, and error states.
- [ ] Empty states guide users toward the next action.
- [ ] All visible buttons, links, filters, and menus work.
- [ ] Mobile layouts do not have unintended horizontal overflow.
- [ ] Keyboard navigation and focus states are supported.
- [ ] No fake statistics, fake companies, or misleading success messages are shown.
- [ ] Private candidate information and resumes are protected by backend permissions.
- [ ] The interface uses real backend data rather than hardcoded production-like values.
- [ ] The website does not look like a plain unstyled template.

## 16. Final Design Instruction

Build **FirstStep Careers — Job Portal for Freshers** as a complete, professional, colorful, and responsive recruitment platform. Follow this design document together with `prd.md`. Prioritize usability, consistency, accessibility, and real functionality. Use reusable components and a centralized design system. Integrate all pages with the Flask backend and MySQL database; do not create a frontend-only mockup. If a feature is not implemented yet, clearly represent it as unavailable rather than pretending it works.

**End of Design Document**
