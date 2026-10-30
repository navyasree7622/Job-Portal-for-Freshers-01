import os
import sqlite3
import pymysql
import pymysql.cursors
from datetime import datetime
from dotenv import load_dotenv

basedir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'job_portal.db')
_USE_SQLITE = None

class SmartDateTime(str):
    def strftime(self, fmt):
        for f in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'):
            try:
                return datetime.strptime(self, f).strftime(fmt)
            except ValueError:
                pass
        return self

def _convert_val(v, key=""):
    if isinstance(v, str):
        # If it looks like a datetime or key indicates a date
        if any(w in key.lower() for w in ('_at', 'date', 'deadline', 'time')) or (len(v) >= 10 and '-' in v[:10]):
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'):
                try:
                    return datetime.strptime(v, fmt)
                except ValueError:
                    pass
            return SmartDateTime(v)
    return v

def _convert_row(r):
    if r is None:
        return None
    d = dict(r)
    for k, v in d.items():
        d[k] = _convert_val(v, k)
    return d

def _init_sqlite_schema(conn):
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'fresher',
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    );
    CREATE TABLE IF NOT EXISTS fresher_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        phone TEXT, location TEXT, education TEXT, degree TEXT, institution TEXT,
        graduation_year INTEGER, cgpa TEXT, skills TEXT, experience_level TEXT DEFAULT 'Fresher (0-1 yr)',
        bio TEXT, github_url TEXT, linkedin_url TEXT, portfolio_url TEXT,
        resume_path TEXT, resume_filename TEXT, updated_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recruiter_user_id INTEGER NOT NULL UNIQUE,
        company_name TEXT NOT NULL, industry TEXT DEFAULT 'Information Technology',
        description TEXT, location TEXT, website TEXT, contact_email TEXT,
        verification_status TEXT DEFAULT 'pending', created_at TEXT DEFAULT (datetime('now', 'localtime')),
        updated_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (recruiter_user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL, recruiter_user_id INTEGER NOT NULL,
        title TEXT NOT NULL, category TEXT NOT NULL DEFAULT 'Software Development',
        description TEXT NOT NULL, responsibilities TEXT, required_skills TEXT NOT NULL,
        eligibility TEXT, location TEXT NOT NULL, job_type TEXT NOT NULL DEFAULT 'Full-Time',
        work_arrangement TEXT NOT NULL DEFAULT 'Onsite', experience_level TEXT NOT NULL DEFAULT 'Fresher (0-1 yr)',
        salary_min INTEGER, salary_max INTEGER, application_deadline TEXT,
        status TEXT NOT NULL DEFAULT 'published', is_featured INTEGER NOT NULL DEFAULT 0,
        is_sample INTEGER NOT NULL DEFAULT 1, views_count INTEGER NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now', 'localtime')), updated_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE,
        FOREIGN KEY (recruiter_user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL, fresher_user_id INTEGER NOT NULL,
        resume_path TEXT NOT NULL, cover_note TEXT, status TEXT NOT NULL DEFAULT 'Applied',
        recruiter_notes TEXT, applied_at TEXT DEFAULT (datetime('now', 'localtime')),
        updated_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
        FOREIGN KEY (fresher_user_id) REFERENCES users (id) ON DELETE CASCADE,
        UNIQUE (job_id, fresher_user_id)
    );
    CREATE TABLE IF NOT EXISTS saved_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fresher_user_id INTEGER NOT NULL, job_id INTEGER NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (fresher_user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE,
        UNIQUE (fresher_user_id, job_id)
    );
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL, title TEXT NOT NULL, message TEXT NOT NULL, link TEXT,
        is_read INTEGER NOT NULL DEFAULT 0, created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reported_by_user_id INTEGER NOT NULL, job_id INTEGER NOT NULL,
        reason TEXT NOT NULL, details TEXT, status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (reported_by_user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, action TEXT NOT NULL, details TEXT,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
    );
    """)
    conn.commit()

def _seed_sqlite_if_empty(conn):
    cur = conn.cursor()
    cur.execute("SELECT count(*) as cnt FROM users")
    if cur.fetchone()[0] == 0:
        print("[Database] Seeding sample data into SQLite...")
        from database.seed_data import seed_database
        seed_database(conn=conn, is_sqlite=True)

def get_db_connection():
    global _USE_SQLITE
    if _USE_SQLITE is None:
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '')
        port = int(os.getenv('MYSQL_PORT', 3306))
        try:
            test_conn = pymysql.connect(host=host, user=user, password=password, port=port, connect_timeout=1)
            test_conn.close()
            _USE_SQLITE = False
            print("[Database] Connected to MySQL successfully.")
        except Exception:
            _USE_SQLITE = True
            print("[Database] MySQL not reachable. Automatically using SQLite database.")

    if _USE_SQLITE:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        conn.create_function("NOW", 0, lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        _init_sqlite_schema(conn)
        _seed_sqlite_if_empty(conn)
        return conn

    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DB', 'job_portal_db')
    port = int(os.getenv('MYSQL_PORT', 3306))
    return pymysql.connect(
        host=host, user=user, password=password, database=database,
        port=port, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, autocommit=False
    )

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            q_str = query.replace('%s', '?')
            cur = conn.cursor()
            cur.execute(q_str, args)
            if one:
                row = cur.fetchone()
                return _convert_row(row) if row else None
            else:
                return [_convert_row(r) for r in cur.fetchall()]
        else:
            with conn.cursor() as cur:
                cur.execute(query, args)
                results = cur.fetchall()
                return (results[0] if results else None) if one else results
    finally:
        conn.close()

def execute_db(query, args=(), return_id=False):
    conn = get_db_connection()
    try:
        if isinstance(conn, sqlite3.Connection):
            q_str = query.replace('%s', '?')
            cur = conn.cursor()
            cur.execute(q_str, args)
            conn.commit()
            if return_id:
                return cur.lastrowid
            return cur.rowcount
        else:
            with conn.cursor() as cur:
                cur.execute(query, args)
                conn.commit()
                if return_id:
                    return cur.lastrowid
                return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
