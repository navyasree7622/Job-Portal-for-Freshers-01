import os
import uuid
from functools import wraps
from datetime import datetime, date
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_from_directory, jsonify, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from database.db import query_db, execute_db

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==========================================================
# Helpers & Decorators
# ==========================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please sign in to access this page.', 'warning')
                return redirect(url_for('login', next=request.path))
            if session.get('role') not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.context_processor
def inject_global_data():
    """Inject unread notifications and user role into all templates."""
    unread_count = 0
    if 'user_id' in session:
        result = query_db(
            "SELECT count(*) as count FROM notifications WHERE user_id = %s AND is_read = 0",
            (session['user_id'],),
            one=True
        )
        if result:
            unread_count = result['count']
    return dict(unread_notif_count=unread_count)

def calculate_fresher_profile_pct(profile):
    """Calculate profile completion percentage based on saved fields."""
    if not profile:
        return 10
    fields = [
        profile.get('phone'),
        profile.get('location'),
        profile.get('education'),
        profile.get('degree'),
        profile.get('institution'),
        profile.get('graduation_year'),
        profile.get('cgpa'),
        profile.get('skills'),
        profile.get('bio'),
        profile.get('github_url'),
        profile.get('linkedin_url'),
    ]
    points = sum(1 for f in fields if f and str(f).strip())
    # Resume is weighted higher (2 points)
    if profile.get('resume_path'):
        points += 2
    total_possible = len(fields) + 2
    return min(100, int((points / total_possible) * 100))

def log_audit_event(user_id, action, details):
    """Record an administrative audit log event in the database."""
    try:
        execute_db(
            "INSERT INTO audit_logs (user_id, action, details, created_at) VALUES (%s, %s, %s, NOW())",
            (user_id, action, details)
        )
    except Exception as e:
        print(f"Audit log warning: {e}")

# ==========================================================
# Public Pages
# ==========================================================

@app.route('/')
def index():
    # Platform metrics for stats ribbon
    stats = {
        'active_jobs': query_db("SELECT count(*) as count FROM jobs WHERE status = 'published'", one=True)['count'],
        'companies_count': query_db("SELECT count(*) as count FROM companies WHERE verification_status = 'verified'", one=True)['count'],
        'freshers_count': query_db("SELECT count(*) as count FROM users WHERE role = 'fresher'", one=True)['count'],
        'applications_count': query_db("SELECT count(*) as count FROM applications", one=True)['count']
    }

    # Category counts for domain cards
    category_counts_raw = query_db("""
        SELECT category, count(*) as count
        FROM jobs
        WHERE status = 'published'
        GROUP BY category
    """)
    cat_counts = {r['category']: r['count'] for r in category_counts_raw}

    # Featured jobs & recent 6 published jobs
    recent_jobs = query_db("""
        SELECT j.*, c.company_name, c.verification_status
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE j.status = 'published'
        ORDER BY j.is_featured DESC, j.created_at DESC
        LIMIT 6
    """)

    # Check bookmarks if fresher is logged in
    saved_ids = set()
    if session.get('role') == 'fresher':
        saved_rows = query_db("SELECT job_id FROM saved_jobs WHERE fresher_user_id = %s", (session['user_id'],))
        saved_ids = {r['job_id'] for r in saved_rows}

    for job in recent_jobs:
        job['is_saved'] = job['id'] in saved_ids

    return render_template('index.html', stats=stats, recent_jobs=recent_jobs, cat_counts=cat_counts)

@app.route('/jobs')
def browse_jobs():
    keyword = request.args.get('keyword', '').strip()
    location = request.args.get('location', '').strip()
    category = request.args.get('category', '').strip()
    job_type = request.args.get('job_type', '').strip()
    work_arrangement = request.args.get('work_arrangement', '').strip()
    experience_level = request.args.get('experience_level', '').strip()
    min_salary = request.args.get('min_salary', '').strip()
    skill = request.args.get('skill', '').strip()
    sort = request.args.get('sort', 'newest').strip()

    sql = """
        SELECT j.*, c.company_name, c.verification_status
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE j.status = 'published'
    """
    params = []

    if keyword:
        sql += " AND (j.title LIKE %s OR j.required_skills LIKE %s OR j.description LIKE %s OR c.company_name LIKE %s)"
        k_param = f"%{keyword}%"
        params.extend([k_param, k_param, k_param, k_param])

    if location:
        if location.lower() == 'remote':
            sql += " AND (j.location LIKE %s OR j.job_type = 'Remote' OR j.work_arrangement = 'Remote')"
            params.append(f"%{location}%")
        else:
            sql += " AND j.location LIKE %s"
            params.append(f"%{location}%")

    if category:
        sql += " AND j.category = %s"
        params.append(category)

    if job_type:
        sql += " AND j.job_type = %s"
        params.append(job_type)

    if work_arrangement:
        sql += " AND j.work_arrangement = %s"
        params.append(work_arrangement)

    if experience_level:
        sql += " AND j.experience_level = %s"
        params.append(experience_level)

    if min_salary and min_salary.isdigit():
        sql += " AND (j.salary_min >= %s OR j.salary_max >= %s)"
        params.extend([int(min_salary), int(min_salary)])

    if skill:
        sql += " AND j.required_skills LIKE %s"
        params.append(f"%{skill}%")

    if sort == 'salary_high':
        sql += " ORDER BY j.salary_max DESC, j.created_at DESC"
    elif sort == 'salary_low':
        sql += " ORDER BY j.salary_min ASC, j.created_at DESC"
    elif sort == 'views':
        sql += " ORDER BY j.views_count DESC, j.created_at DESC"
    elif sort == 'title_asc':
        sql += " ORDER BY j.title ASC"
    else:
        sql += " ORDER BY j.is_featured DESC, j.created_at DESC"

    jobs = query_db(sql, tuple(params))

    # Aggregated counts for faceted sidebar
    cat_counts_raw = query_db("""
        SELECT category, count(*) as count
        FROM jobs
        WHERE status = 'published'
        GROUP BY category
        ORDER BY count DESC
    """)
    category_counts = {r['category']: r['count'] for r in cat_counts_raw}

    arr_counts_raw = query_db("""
        SELECT work_arrangement, count(*) as count
        FROM jobs
        WHERE status = 'published' AND work_arrangement IS NOT NULL
        GROUP BY work_arrangement
    """)
    arrangement_counts = {r['work_arrangement']: r['count'] for r in arr_counts_raw}

    types_counts_raw = query_db("""
        SELECT job_type, count(*) as count
        FROM jobs
        WHERE status = 'published'
        GROUP BY job_type
    """)
    type_counts = {r['job_type']: r['count'] for r in types_counts_raw}

    # Check bookmarks for fresher
    saved_ids = set()
    if session.get('role') == 'fresher':
        saved_rows = query_db("SELECT job_id FROM saved_jobs WHERE fresher_user_id = %s", (session['user_id'],))
        saved_ids = {r['job_id'] for r in saved_rows}

    for job in jobs:
        job['is_saved'] = job['id'] in saved_ids

    filters = {
        'keyword': keyword,
        'location': location,
        'category': category,
        'job_type': job_type,
        'work_arrangement': work_arrangement,
        'experience_level': experience_level,
        'min_salary': min_salary,
        'skill': skill,
        'sort': sort
    }

    # Popular skill pills for quick clicking
    popular_skills = [
        'Python', 'Java', 'SQL', 'React', 'Flask', 'Pandas',
        'Power BI', 'Figma', 'Selenium', 'Docker', 'AWS', 'Linux'
    ]

    return render_template(
        'jobs.html',
        jobs=jobs,
        filters=filters,
        category_counts=category_counts,
        arrangement_counts=arrangement_counts,
        type_counts=type_counts,
        popular_skills=popular_skills
    )

@app.route('/jobs/<int:job_id>')
def job_details(job_id):
    # Fetch job and increment view count
    execute_db("UPDATE jobs SET views_count = views_count + 1 WHERE id = %s", (job_id,))
    
    job = query_db("""
        SELECT j.*, c.company_name, c.description as company_description,
               c.website, c.verification_status
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE j.id = %s
    """, (job_id,), one=True)

    if not job:
        abort(404)

    is_saved = False
    existing_application = None
    profile = None

    if session.get('role') == 'fresher':
        user_id = session['user_id']
        # Check bookmark
        is_saved = bool(query_db("SELECT id FROM saved_jobs WHERE fresher_user_id = %s AND job_id = %s", (user_id, job_id), one=True))
        # Check previous application
        existing_application = query_db("SELECT * FROM applications WHERE fresher_user_id = %s AND job_id = %s", (user_id, job_id), one=True)
        # Fetch profile
        profile = query_db("SELECT * FROM fresher_profiles WHERE user_id = %s", (user_id,), one=True)

    return render_template(
        'job_details.html',
        job=job,
        is_saved=is_saved,
        existing_application=existing_application,
        profile=profile
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ==========================================================
# Authentication & Registration
# ==========================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'fresher':
            return redirect(url_for('fresher_dashboard'))
        elif role == 'recruiter':
            return redirect(url_for('recruiter_dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        next_url = request.form.get('next', '').strip()

        user = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)

        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid email address or password. Please try again.', 'error')
            return render_template('login.html')

        if not user['is_active']:
            flash('Your account has been suspended by an administrator. Please contact support.', 'error')
            return render_template('login.html')

        # Set session details
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['email'] = user['email']
        session['role'] = user['role']

        flash(f'Welcome back, {user["name"]}!', 'success')

        if next_url and next_url.startswith('/'):
            return redirect(next_url)

        if user['role'] == 'fresher':
            return redirect(url_for('fresher_dashboard'))
        elif user['role'] == 'recruiter':
            return redirect(url_for('recruiter_dashboard'))
        elif user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'fresher')
        company_name = request.form.get('company_name', '').strip()

        # Validation
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match. Please retype carefully.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters in length.', 'error')
            return render_template('register.html')

        if role not in ['fresher', 'recruiter']:
            role = 'fresher'

        # Check existing user
        existing = query_db("SELECT id FROM users WHERE email = %s", (email,), one=True)
        if existing:
            flash('An account with this email address already exists. Please sign in.', 'error')
            return render_template('register.html')

        # Insert user
        password_hash = generate_password_hash(password)
        user_id = execute_db(
            "INSERT INTO users (name, email, password_hash, role, is_active, created_at) VALUES (%s, %s, %s, %s, 1, NOW())",
            (name, email, password_hash, role),
            return_id=True
        )

        if role == 'fresher':
            # Create initial empty fresher profile
            execute_db("INSERT INTO fresher_profiles (user_id) VALUES (%s)", (user_id,))
            flash('Registration successful! Please complete your profile and upload your resume.', 'success')
        elif role == 'recruiter':
            # Create company record
            c_name = company_name if company_name else f"{name}'s Organization"
            execute_db(
                "INSERT INTO companies (recruiter_user_id, company_name, verification_status, created_at) VALUES (%s, %s, 'pending', NOW())",
                (user_id, c_name)
            )
            flash('Recruiter account created! Company verification is currently pending review.', 'success')

        # Automatically sign in
        session['user_id'] = user_id
        session['user_name'] = name
        session['email'] = email
        session['role'] = role

        if role == 'fresher':
            return redirect(url_for('fresher_profile'))
        else:
            return redirect(url_for('company_profile'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('index'))

# ==========================================================
# Fresher Workflows
# ==========================================================

@app.route('/fresher/dashboard')
@role_required('fresher')
def fresher_dashboard():
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    profile = query_db("SELECT * FROM fresher_profiles WHERE user_id = %s", (user_id,), one=True)

    profile_pct = calculate_fresher_profile_pct(profile)

    metrics = {
        'total_applications': query_db("SELECT count(*) as count FROM applications WHERE fresher_user_id = %s", (user_id,), one=True)['count'],
        'under_review': query_db("SELECT count(*) as count FROM applications WHERE fresher_user_id = %s AND status = 'Under Review'", (user_id,), one=True)['count'],
        'shortlisted': query_db("SELECT count(*) as count FROM applications WHERE fresher_user_id = %s AND status = 'Shortlisted'", (user_id,), one=True)['count'],
        'interviews': query_db("SELECT count(*) as count FROM applications WHERE fresher_user_id = %s AND status = 'Interview Scheduled'", (user_id,), one=True)['count'],
        'selected': query_db("SELECT count(*) as count FROM applications WHERE fresher_user_id = %s AND status = 'Selected'", (user_id,), one=True)['count'],
        'saved_jobs': query_db("SELECT count(*) as count FROM saved_jobs WHERE fresher_user_id = %s", (user_id,), one=True)['count']
    }

    recent_applications = query_db("""
        SELECT a.*, j.title, c.company_name, j.location, j.job_type, j.work_arrangement
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE a.fresher_user_id = %s
        ORDER BY a.applied_at DESC
        LIMIT 5
    """, (user_id,))

    # Skill-Based Matching Recommendation Algorithm
    recommended_jobs = []
    if profile and profile.get('skills'):
        skills_raw = profile['skills'].split(',')
        skills_clean = [s.strip() for s in skills_raw if len(s.strip()) > 1]
        if skills_clean:
            like_parts = " OR ".join(["j.required_skills LIKE %s OR j.title LIKE %s" for _ in skills_clean])
            params = []
            for s in skills_clean:
                params.extend([f"%{s}%", f"%{s}%"])
            params.append(user_id)
            recommended_jobs = query_db(f"""
                SELECT j.*, c.company_name, c.verification_status
                FROM jobs j
                JOIN companies c ON j.company_id = c.id
                WHERE j.status = 'published'
                  AND ({like_parts})
                  AND j.id NOT IN (SELECT job_id FROM applications WHERE fresher_user_id = %s)
                ORDER BY j.is_featured DESC, j.created_at DESC
                LIMIT 4
            """, tuple(params))

    # Fallback to newest openings if fewer recommendations
    if len(recommended_jobs) < 4:
        rec_ids = [rj['id'] for rj in recommended_jobs]
        exclude_clause = ""
        params = [user_id]
        if rec_ids:
            exclude_clause = f"AND j.id NOT IN ({','.join(['%s'] * len(rec_ids))})"
            params = [user_id] + rec_ids

        more_jobs = query_db(f"""
            SELECT j.*, c.company_name, c.verification_status
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.status = 'published'
              AND j.id NOT IN (SELECT job_id FROM applications WHERE fresher_user_id = %s)
              {exclude_clause}
            ORDER BY j.created_at DESC
            LIMIT {4 - len(recommended_jobs)}
        """, tuple(params))
        recommended_jobs.extend(more_jobs)

    # Check bookmarks
    saved_rows = query_db("SELECT job_id FROM saved_jobs WHERE fresher_user_id = %s", (user_id,))
    saved_ids = {r['job_id'] for r in saved_rows}
    for rj in recommended_jobs:
        rj['is_saved'] = rj['id'] in saved_ids

    # Recent notifications for dashboard widget
    recent_notifications = query_db("""
        SELECT * FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 4
    """, (user_id,))

    # Recent saved jobs for quick access
    recent_saved = query_db("""
        SELECT j.*, c.company_name
        FROM saved_jobs s
        JOIN jobs j ON s.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE s.fresher_user_id = %s
        ORDER BY s.created_at DESC
        LIMIT 3
    """, (user_id,))

    return render_template(
        'fresher_dashboard.html',
        user=user,
        profile=profile,
        profile_pct=profile_pct,
        metrics=metrics,
        recent_applications=recent_applications,
        recommended_jobs=recommended_jobs,
        recent_notifications=recent_notifications,
        recent_saved=recent_saved
    )

@app.route('/fresher/profile', methods=['GET', 'POST'])
@role_required('fresher')
def fresher_profile():
    user_id = session['user_id']
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    profile = query_db("SELECT * FROM fresher_profiles WHERE user_id = %s", (user_id,), one=True)

    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        education = request.form.get('education', '').strip()
        degree = request.form.get('degree', '').strip()
        institution = request.form.get('institution', '').strip()
        graduation_year = request.form.get('graduation_year', None)
        cgpa = request.form.get('cgpa', '').strip()
        skills = request.form.get('skills', '').strip()
        bio = request.form.get('bio', '').strip()
        github_url = request.form.get('github_url', '').strip()
        linkedin_url = request.form.get('linkedin_url', '').strip()
        portfolio_url = request.form.get('portfolio_url', '').strip()

        resume_path = profile.get('resume_path') if profile else None
        resume_filename = profile.get('resume_filename') if profile else None

        # Check resume upload
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    original_name = secure_filename(file.filename)
                    unique_name = f"{uuid.uuid4().hex}_{original_name}"
                    file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                    file.save(file_save_path)
                    resume_path = unique_name
                    resume_filename = original_name
                else:
                    flash('Invalid resume file format. Only .pdf, .doc, and .docx files are allowed.', 'error')
                    return redirect(url_for('fresher_profile'))

        # Update profile in MySQL
        execute_db("""
            UPDATE fresher_profiles SET
                phone = %s,
                location = %s,
                education = %s,
                degree = %s,
                institution = %s,
                graduation_year = %s,
                cgpa = %s,
                skills = %s,
                bio = %s,
                github_url = %s,
                linkedin_url = %s,
                portfolio_url = %s,
                resume_path = %s,
                resume_filename = %s
            WHERE user_id = %s
        """, (
            phone, location, education, degree, institution,
            int(graduation_year) if graduation_year else None,
            cgpa, skills, bio, github_url, linkedin_url, portfolio_url,
            resume_path, resume_filename, user_id
        ))

        flash('Your profile and resume details have been updated successfully!', 'success')
        return redirect(url_for('fresher_profile'))

    profile_pct = calculate_fresher_profile_pct(profile)
    return render_template('profile.html', user=user, profile=profile, profile_pct=profile_pct)

@app.route('/fresher/applications')
@role_required('fresher')
def my_applications():
    user_id = session['user_id']
    applications = query_db("""
        SELECT a.*, j.title, j.location, c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE a.fresher_user_id = %s
        ORDER BY a.applied_at DESC
    """, (user_id,))

    return render_template('applications.html', applications=applications)

@app.route('/fresher/applications/<int:application_id>/withdraw', methods=['POST'])
@role_required('fresher')
def withdraw_application(application_id):
    user_id = session['user_id']
    app_record = query_db(
        "SELECT * FROM applications WHERE id = %s AND fresher_user_id = %s",
        (application_id, user_id),
        one=True
    )
    if not app_record:
        abort(404)

    execute_db("UPDATE applications SET status = 'Withdrawn' WHERE id = %s", (application_id,))
    flash('Your job application has been withdrawn.', 'info')
    return redirect(url_for('my_applications'))

@app.route('/fresher/saved-jobs')
@role_required('fresher')
def saved_jobs():
    user_id = session['user_id']
    saved = query_db("""
        SELECT j.*, c.company_name, s.created_at as saved_at
        FROM saved_jobs s
        JOIN jobs j ON s.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE s.fresher_user_id = %s
        ORDER BY s.created_at DESC
    """, (user_id,))

    return render_template('saved_jobs.html', saved_jobs=saved)

@app.route('/jobs/<int:job_id>/apply', methods=['POST'])
@role_required('fresher')
def apply_job(job_id):
    user_id = session['user_id']
    cover_note = request.form.get('cover_note', '').strip()
    use_existing_resume = request.form.get('use_existing_resume') == '1'

    # Check if job is valid and published
    job = query_db("SELECT * FROM jobs WHERE id = %s", (job_id,), one=True)
    if not job or job['status'] != 'published':
        flash('This job opening is no longer accepting applications.', 'error')
        return redirect(url_for('job_details', job_id=job_id))

    # Check duplicate application
    existing = query_db("SELECT id FROM applications WHERE job_id = %s AND fresher_user_id = %s", (job_id, user_id), one=True)
    if existing:
        flash('You have already submitted an application for this position.', 'warning')
        return redirect(url_for('job_details', job_id=job_id))

    profile = query_db("SELECT * FROM fresher_profiles WHERE user_id = %s", (user_id,), one=True)
    resume_path = None

    if use_existing_resume and profile and profile.get('resume_path'):
        resume_path = profile['resume_path']
    elif 'resume_file' in request.files and request.files['resume_file'].filename != '':
        file = request.files['resume_file']
        if allowed_file(file.filename):
            original_name = secure_filename(file.filename)
            unique_name = f"{uuid.uuid4().hex}_{original_name}"
            file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(file_save_path)
            resume_path = unique_name
            # Also update profile if it was empty
            if not profile.get('resume_path'):
                execute_db("UPDATE fresher_profiles SET resume_path = %s, resume_filename = %s WHERE user_id = %s", (unique_name, original_name, user_id))
        else:
            flash('Invalid resume file format. Allowed formats: PDF, DOC, DOCX.', 'error')
            return redirect(url_for('job_details', job_id=job_id))
    elif profile and profile.get('resume_path'):
        resume_path = profile['resume_path']

    if not resume_path:
        flash('Please upload your resume to apply for this job.', 'error')
        return redirect(url_for('job_details', job_id=job_id))

    # Insert application
    execute_db("""
        INSERT INTO applications (job_id, fresher_user_id, resume_path, cover_note, status, applied_at)
        VALUES (%s, %s, %s, %s, 'Applied', NOW())
    """, (job_id, user_id, resume_path, cover_note))

    # Send in-portal notification to the recruiter
    execute_db("""
        INSERT INTO notifications (user_id, title, message, link, is_read, created_at)
        VALUES (%s, %s, %s, %s, 0, NOW())
    """, (
        job['recruiter_user_id'],
        'New Candidate Application',
        f"{session.get('user_name')} applied for {job['title']}.",
        f"/recruiter/applicants?job_id={job_id}"
    ))

    flash('Congratulations! Your application has been submitted successfully.', 'success')
    return redirect(url_for('my_applications'))

@app.route('/jobs/<int:job_id>/report', methods=['POST'])
@login_required
def report_job(job_id):
    user_id = session['user_id']
    reason = request.form.get('reason', '').strip()
    details = request.form.get('details', '').strip()

    if not reason:
        flash('Please select a valid report reason.', 'error')
        return redirect(url_for('job_details', job_id=job_id))

    execute_db("""
        INSERT INTO reports (reported_by_user_id, job_id, reason, details, status, created_at)
        VALUES (%s, %s, %s, %s, 'pending', NOW())
    """, (user_id, job_id, reason, details))

    flash('Thank you. Your report has been submitted to the moderation team for investigation.', 'info')
    return redirect(url_for('job_details', job_id=job_id))

# ==========================================================
# Recruiter Workflows
# ==========================================================

@app.route('/recruiter/dashboard')
@role_required('recruiter')
def recruiter_dashboard():
    user_id = session['user_id']
    company = query_db("SELECT * FROM companies WHERE recruiter_user_id = %s", (user_id,), one=True)
    if not company:
        flash('Please complete your company profile to start hiring.', 'info')
        return redirect(url_for('company_profile'))

    metrics = {
        'active_jobs': query_db("SELECT count(*) as count FROM jobs WHERE recruiter_user_id = %s AND status = 'published'", (user_id,), one=True)['count'],
        'closed_jobs': query_db("SELECT count(*) as count FROM jobs WHERE recruiter_user_id = %s AND status = 'closed'", (user_id,), one=True)['count'],
        'total_applicants': query_db("""
            SELECT count(*) as count
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE j.recruiter_user_id = %s
        """, (user_id,), one=True)['count'],
        'under_review': query_db("""
            SELECT count(*) as count
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE j.recruiter_user_id = %s AND a.status = 'Under Review'
        """, (user_id,), one=True)['count'],
        'shortlisted': query_db("""
            SELECT count(*) as count
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE j.recruiter_user_id = %s AND a.status = 'Shortlisted'
        """, (user_id,), one=True)['count'],
        'interviews': query_db("""
            SELECT count(*) as count
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE j.recruiter_user_id = %s AND a.status = 'Interview Scheduled'
        """, (user_id,), one=True)['count'],
        'selected': query_db("""
            SELECT count(*) as count
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE j.recruiter_user_id = %s AND a.status = 'Selected'
        """, (user_id,), one=True)['count']
    }

    # Recruiter's jobs with applicant counts
    jobs = query_db("""
        SELECT j.*, count(a.id) as applicant_count
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
        WHERE j.recruiter_user_id = %s
        GROUP BY j.id
        ORDER BY j.created_at DESC
        LIMIT 6
    """, (user_id,))

    # Recent applicants
    recent_applications = query_db("""
        SELECT a.*, u.name as candidate_name, u.email as candidate_email,
               fp.education, fp.degree, fp.graduation_year, fp.skills, j.title as job_title
        FROM applications a
        JOIN users u ON a.fresher_user_id = u.id
        LEFT JOIN fresher_profiles fp ON u.id = fp.user_id
        JOIN jobs j ON a.job_id = j.id
        WHERE j.recruiter_user_id = %s
        ORDER BY a.applied_at DESC
        LIMIT 5
    """, (user_id,))

    # Recruiter notifications
    recent_notifications = query_db("""
        SELECT * FROM notifications
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 4
    """, (user_id,))

    return render_template(
        'recruiter_dashboard.html',
        company=company,
        metrics=metrics,
        jobs=jobs,
        recent_applications=recent_applications,
        recent_notifications=recent_notifications
    )

@app.route('/recruiter/company-profile', methods=['GET', 'POST'])
@role_required('recruiter')
def company_profile():
    user_id = session['user_id']
    company = query_db("SELECT * FROM companies WHERE recruiter_user_id = %s", (user_id,), one=True)

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        industry = request.form.get('industry', '').strip()
        website = request.form.get('website', '').strip()
        location = request.form.get('location', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        description = request.form.get('description', '').strip()

        if not company_name:
            flash('Company name is required.', 'error')
            return render_template('company_profile.html', company=company)

        if company:
            execute_db("""
                UPDATE companies SET
                    company_name = %s,
                    industry = %s,
                    website = %s,
                    location = %s,
                    contact_email = %s,
                    description = %s
                WHERE id = %s
            """, (company_name, industry, website, location, contact_email, description, company['id']))
        else:
            execute_db("""
                INSERT INTO companies (recruiter_user_id, company_name, industry, website, location, contact_email, description, verification_status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
            """, (user_id, company_name, industry, website, location, contact_email, description))

        flash('Company profile details saved successfully!', 'success')
        return redirect(url_for('company_profile'))

    return render_template('company_profile.html', company=company)

@app.route('/recruiter/jobs')
@role_required('recruiter')
def manage_jobs():
    user_id = session['user_id']
    jobs = query_db("""
        SELECT j.*, count(a.id) as applicant_count
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
        WHERE j.recruiter_user_id = %s
        GROUP BY j.id
        ORDER BY j.created_at DESC
    """, (user_id,))

    return render_template('manage_jobs.html', jobs=jobs)

@app.route('/recruiter/jobs/post', methods=['GET', 'POST'])
@role_required('recruiter')
def post_job():
    user_id = session['user_id']
    company = query_db("SELECT * FROM companies WHERE recruiter_user_id = %s", (user_id,), one=True)
    if not company:
        flash('Please setup your company profile first before posting vacancies.', 'warning')
        return redirect(url_for('company_profile'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Software Development').strip()
        job_type = request.form.get('job_type', 'Full-Time').strip()
        work_arrangement = request.form.get('work_arrangement', 'Onsite').strip()
        experience_level = request.form.get('experience_level', 'Fresher (0-1 yr)').strip()
        location = request.form.get('location', '').strip()
        salary_min = request.form.get('salary_min') or None
        salary_max = request.form.get('salary_max') or None
        application_deadline = request.form.get('application_deadline') or None
        required_skills = request.form.get('required_skills', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        description = request.form.get('description', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()
        status = request.form.get('status', 'published').strip()
        is_featured = 1 if request.form.get('is_featured') == '1' else 0

        if not title or not location or not required_skills or not description:
            flash('Please complete all mandatory job fields.', 'error')
            return render_template('post_job.html', job=None)

        execute_db("""
            INSERT INTO jobs (
                company_id, recruiter_user_id, title, category, description,
                responsibilities, required_skills, eligibility, location,
                job_type, work_arrangement, experience_level, salary_min, salary_max,
                application_deadline, status, is_featured, is_sample, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, NOW())
        """, (
            company['id'], user_id, title, category, description,
            responsibilities, required_skills, eligibility, location,
            job_type, work_arrangement, experience_level,
            int(salary_min) if salary_min else None,
            int(salary_max) if salary_max else None,
            application_deadline if application_deadline else None,
            status, is_featured
        ))

        flash(f'Job opening "{title}" has been successfully published!', 'success')
        return redirect(url_for('manage_jobs'))

    return render_template('post_job.html', job=None)

@app.route('/recruiter/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@role_required('recruiter')
def edit_job(job_id):
    user_id = session['user_id']
    job = query_db("SELECT * FROM jobs WHERE id = %s AND recruiter_user_id = %s", (job_id, user_id), one=True)
    if not job:
        abort(404)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        job_type = request.form.get('job_type', '').strip()
        work_arrangement = request.form.get('work_arrangement', 'Onsite').strip()
        experience_level = request.form.get('experience_level', '').strip()
        location = request.form.get('location', '').strip()
        salary_min = request.form.get('salary_min') or None
        salary_max = request.form.get('salary_max') or None
        application_deadline = request.form.get('application_deadline') or None
        required_skills = request.form.get('required_skills', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        description = request.form.get('description', '').strip()
        responsibilities = request.form.get('responsibilities', '').strip()
        status = request.form.get('status', 'published').strip()
        is_featured = 1 if request.form.get('is_featured') == '1' else 0

        execute_db("""
            UPDATE jobs SET
                title = %s,
                category = %s,
                job_type = %s,
                work_arrangement = %s,
                experience_level = %s,
                location = %s,
                salary_min = %s,
                salary_max = %s,
                application_deadline = %s,
                required_skills = %s,
                eligibility = %s,
                description = %s,
                responsibilities = %s,
                status = %s,
                is_featured = %s
            WHERE id = %s AND recruiter_user_id = %s
        """, (
            title, category, job_type, work_arrangement, experience_level, location,
            int(salary_min) if salary_min else None,
            int(salary_max) if salary_max else None,
            application_deadline if application_deadline else None,
            required_skills, eligibility, description, responsibilities,
            status, is_featured, job_id, user_id
        ))

        flash(f'Job "{title}" has been updated successfully.', 'success')
        return redirect(url_for('manage_jobs'))

    return render_template('post_job.html', job=job)

@app.route('/recruiter/jobs/<int:job_id>/toggle-status', methods=['POST'])
@role_required('recruiter')
def toggle_job_status(job_id):
    user_id = session['user_id']
    new_status = request.form.get('new_status', 'closed')
    execute_db(
        "UPDATE jobs SET status = %s WHERE id = %s AND recruiter_user_id = %s",
        (new_status, job_id, user_id)
    )
    flash(f'Job status changed to {new_status}.', 'info')
    return redirect(url_for('manage_jobs'))

@app.route('/recruiter/applicants')
@role_required('recruiter')
def recruiter_applicants():
    user_id = session['user_id']
    selected_job_id = request.args.get('job_id', '').strip()
    selected_status = request.args.get('status', '').strip()

    # Recruiter jobs for the dropdown
    recruiter_jobs = query_db("""
        SELECT j.id, j.title, count(a.id) as applicant_count
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
        WHERE j.recruiter_user_id = %s
        GROUP BY j.id
        ORDER BY j.title ASC
    """, (user_id,))

    sql = """
        SELECT a.*, u.name as candidate_name, u.email as candidate_email,
               fp.phone, fp.location, fp.education, fp.degree,
               fp.institution, fp.graduation_year, fp.cgpa, fp.skills,
               j.title as job_title
        FROM applications a
        JOIN users u ON a.fresher_user_id = u.id
        LEFT JOIN fresher_profiles fp ON u.id = fp.user_id
        JOIN jobs j ON a.job_id = j.id
        WHERE j.recruiter_user_id = %s
    """
    params = [user_id]

    if selected_job_id:
        sql += " AND j.id = %s"
        params.append(selected_job_id)

    if selected_status:
        sql += " AND a.status = %s"
        params.append(selected_status)

    sql += " ORDER BY a.applied_at DESC"

    applicants = query_db(sql, tuple(params))

    return render_template(
        'applicants.html',
        recruiter_jobs=recruiter_jobs,
        applicants=applicants,
        selected_job_id=selected_job_id,
        selected_status=selected_status
    )

@app.route('/recruiter/applications/<int:application_id>/status', methods=['POST'])
@role_required('recruiter')
def update_applicant_status(application_id):
    user_id = session['user_id']
    new_status = request.form.get('status', 'Under Review')
    recruiter_notes = request.form.get('recruiter_notes', '').strip()
    return_job_id = request.form.get('return_job_id', '')
    return_status = request.form.get('return_status', '')

    # Verify that this application belongs to a job posted by this recruiter
    app_record = query_db("""
        SELECT a.*, j.title, j.recruiter_user_id, c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE a.id = %s AND j.recruiter_user_id = %s
    """, (application_id, user_id), one=True)

    if not app_record:
        abort(403)

    # Update application
    execute_db("""
        UPDATE applications SET status = %s, recruiter_notes = %s, updated_at = NOW()
        WHERE id = %s
    """, (new_status, recruiter_notes, application_id))

    # Send in-portal notification to the applicant
    notif_msg = f"{app_record['company_name']} updated your application status for '{app_record['title']}' to '{new_status}'."
    if recruiter_notes:
        notif_msg += f" Note: {recruiter_notes}"

    execute_db("""
        INSERT INTO notifications (user_id, title, message, link, is_read, created_at)
        VALUES (%s, %s, %s, %s, 0, NOW())
    """, (
        app_record['fresher_user_id'],
        f"Application Update: {new_status}",
        notif_msg,
        "/fresher/applications"
    ))

    flash(f"Candidate status updated to '{new_status}' and notified.", 'success')

    redirect_url = url_for('recruiter_applicants')
    query_params = []
    if return_job_id:
        query_params.append(f"job_id={return_job_id}")
    if return_status:
        query_params.append(f"status={return_status}")
    if query_params:
        redirect_url += '?' + '&'.join(query_params)

    return redirect(redirect_url)

# ==========================================================
# Admin Workflows
# ==========================================================

@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    metrics = {
        'total_users': query_db("SELECT count(*) as count FROM users", one=True)['count'],
        'total_freshers': query_db("SELECT count(*) as count FROM users WHERE role = 'fresher'", one=True)['count'],
        'total_recruiters': query_db("SELECT count(*) as count FROM users WHERE role = 'recruiter'", one=True)['count'],
        'total_jobs': query_db("SELECT count(*) as count FROM jobs", one=True)['count'],
        'active_jobs': query_db("SELECT count(*) as count FROM jobs WHERE status = 'published'", one=True)['count'],
        'total_applications': query_db("SELECT count(*) as count FROM applications", one=True)['count'],
        'pending_companies': query_db("SELECT count(*) as count FROM companies WHERE verification_status = 'pending'", one=True)['count'],
        'total_reports': query_db("SELECT count(*) as count FROM reports", one=True)['count'],
        'pending_reports': query_db("SELECT count(*) as count FROM reports WHERE status = 'pending'", one=True)['count']
    }

    recent_users = query_db("SELECT * FROM users ORDER BY created_at DESC LIMIT 6")

    recent_audit_logs = query_db("""
        SELECT a.*, u.name as user_name, u.email as user_email
        FROM audit_logs a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.created_at DESC
        LIMIT 6
    """)

    category_stats = query_db("""
        SELECT category, count(*) as count
        FROM jobs
        GROUP BY category
        ORDER BY count DESC
    """)

    return render_template(
        'admin_dashboard.html',
        metrics=metrics,
        recent_users=recent_users,
        recent_audit_logs=recent_audit_logs,
        category_stats=category_stats
    )

@app.route('/admin/users')
@role_required('admin')
def admin_users():
    role = request.args.get('role', '').strip()
    if role in ['fresher', 'recruiter', 'admin']:
        users = query_db("SELECT * FROM users WHERE role = %s ORDER BY created_at DESC", (role,))
    else:
        users = query_db("SELECT * FROM users ORDER BY created_at DESC")
    return render_template('admin_users.html', users=users, selected_role=role)

@app.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@role_required('admin')
def admin_toggle_user(user_id):
    if user_id == session.get('user_id'):
        flash('You cannot suspend your own admin account.', 'error')
        return redirect(url_for('admin_users'))

    user = query_db("SELECT email, is_active FROM users WHERE id = %s", (user_id,), one=True)
    if user:
        new_status = 0 if user['is_active'] else 1
        execute_db("UPDATE users SET is_active = %s WHERE id = %s", (new_status, user_id))
        action_name = 'Activated Account' if new_status else 'Suspended Account'
        log_audit_event(session['user_id'], action_name, f"User {user['email']} set to {'active' if new_status else 'suspended'}")
        msg = 'Account has been activated.' if new_status else 'Account has been suspended.'
        flash(msg, 'info')

    return_role = request.form.get('return_role', '')
    if return_role:
        return redirect(url_for('admin_users', role=return_role))
    return redirect(url_for('admin_users'))

@app.route('/admin/companies')
@role_required('admin')
def admin_companies():
    companies = query_db("""
        SELECT c.*, u.name as recruiter_name, u.email as recruiter_email
        FROM companies c
        JOIN users u ON c.recruiter_user_id = u.id
        ORDER BY c.created_at DESC
    """)
    return render_template('admin_companies.html', companies=companies)

@app.route('/admin/companies/<int:company_id>/verify', methods=['POST'])
@role_required('admin')
def admin_verify_company(company_id):
    status = request.form.get('status', 'verified')
    comp = query_db("SELECT company_name FROM companies WHERE id = %s", (company_id,), one=True)
    execute_db("UPDATE companies SET verification_status = %s WHERE id = %s", (status, company_id))
    c_name = comp['company_name'] if comp else f"ID {company_id}"
    log_audit_event(session['user_id'], 'Company Verification Updated', f"{c_name} marked as {status}")
    flash(f'Company status updated to {status}.', 'success')
    return redirect(url_for('admin_companies'))

@app.route('/admin/jobs')
@role_required('admin')
def admin_jobs():
    jobs = query_db("""
        SELECT j.*, c.company_name, count(a.id) as applicant_count
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        LEFT JOIN applications a ON j.id = a.job_id
        GROUP BY j.id
        ORDER BY j.created_at DESC
    """)
    return render_template('admin_jobs.html', jobs=jobs)

@app.route('/admin/jobs/<int:job_id>/moderate', methods=['POST'])
@role_required('admin')
def admin_moderate_job(job_id):
    action = request.form.get('action')
    job = query_db("SELECT title FROM jobs WHERE id = %s", (job_id,), one=True)
    j_title = job['title'] if job else f"Job #{job_id}"
    if action == 'delete':
        execute_db("DELETE FROM jobs WHERE id = %s", (job_id,))
        log_audit_event(session['user_id'], 'Deleted Job Posting', f"Permanently removed job: '{j_title}'")
        flash('Job posting permanently deleted.', 'info')
    elif action == 'close':
        execute_db("UPDATE jobs SET status = 'closed' WHERE id = %s", (job_id,))
        log_audit_event(session['user_id'], 'Closed Job Posting', f"Closed vacancy: '{j_title}'")
        flash('Job posting closed.', 'info')
    elif action == 'publish':
        execute_db("UPDATE jobs SET status = 'published' WHERE id = %s", (job_id,))
        log_audit_event(session['user_id'], 'Published Job Posting', f"Approved/Re-published: '{j_title}'")
        flash('Job posting re-published.', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/reports')
@role_required('admin')
def admin_reports():
    reports = query_db("""
        SELECT r.*, u.name as reporter_name, u.email as reporter_email,
               j.title as job_title, c.company_name
        FROM reports r
        JOIN users u ON r.reported_by_user_id = u.id
        JOIN jobs j ON r.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        ORDER BY r.created_at DESC
    """)
    return render_template('admin_reports.html', reports=reports)

@app.route('/admin/reports/<int:report_id>/handle', methods=['POST'])
@role_required('admin')
def admin_handle_report(report_id):
    status = request.form.get('status', 'resolved')
    execute_db("UPDATE reports SET status = %s WHERE id = %s", (status, report_id))
    log_audit_event(session['user_id'], 'Safety Report Processed', f"Report #{report_id} status set to {status}")
    flash(f'Report marked as {status}.', 'info')
    return redirect(url_for('admin_reports'))

# ==========================================================
# In-Portal Notifications & Bookmark API
# ==========================================================

@app.route('/notifications')
@login_required
def notifications():
    user_id = session['user_id']
    notifs = query_db("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    # Mark as read upon opening page
    execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = %s", (user_id,))
    return render_template('notifications.html', notifications=notifs)

@app.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = %s", (session['user_id'],))
    flash('All notifications marked as read.', 'info')
    return redirect(url_for('notifications'))

@app.route('/api/jobs/<int:job_id>/bookmark', methods=['POST'])
def api_toggle_bookmark(job_id):
    if 'user_id' not in session or session.get('role') != 'fresher':
        return jsonify({'status': 'unauthorized'}), 401

    user_id = session['user_id']
    existing = query_db("SELECT id FROM saved_jobs WHERE fresher_user_id = %s AND job_id = %s", (user_id, job_id), one=True)

    if existing:
        execute_db("DELETE FROM saved_jobs WHERE id = %s", (existing['id'],))
        return jsonify({'status': 'removed', 'job_id': job_id})
    else:
        execute_db("INSERT INTO saved_jobs (fresher_user_id, job_id, created_at) VALUES (%s, %s, NOW())", (user_id, job_id))
        return jsonify({'status': 'saved', 'job_id': job_id})

# ==========================================================
# Secure Resume Download Handler
# ==========================================================

@app.route('/uploads/resume/<filename>')
@login_required
def download_resume(filename):
    """
    Secure file access control:
    Only allowed for:
    1. The candidate who owns the resume.
    2. A recruiter whose job opening the candidate applied to.
    3. An administrator.
    """
    current_user_id = session['user_id']
    current_role = session['role']

    # Admin is authorized
    if current_role == 'admin':
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

    # If candidate owns this resume
    fresher = query_db("SELECT user_id FROM fresher_profiles WHERE resume_path = %s", (filename,), one=True)
    if fresher and fresher['user_id'] == current_user_id:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

    # If recruiter owns the job where this resume was submitted
    if current_role == 'recruiter':
        authorized_recruiter = query_db("""
            SELECT j.recruiter_user_id
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE a.resume_path = %s AND j.recruiter_user_id = %s
        """, (filename, current_user_id), one=True)

        if authorized_recruiter:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)

    abort(403)

# ==========================================================
# Custom Error Handlers
# ==========================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

