import os
import pymysql
import pymysql.cursors
from flask import current_app, g

def get_db_connection():
    """Create and return a new database connection."""
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DB', 'job_portal_db')
    port = int(os.getenv('MYSQL_PORT', 3306))

    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return connection
    except pymysql.err.OperationalError as e:
        # If database does not exist, try to create it
        if e.args[0] == 1049:  # Unknown database
            temp_conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                port=port,
                charset='utf8mb4'
            )
            with temp_conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            temp_conn.close()
            # Retry connection with database
            return pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
        raise e

def query_db(query, args=(), one=False):
    """Execute a SELECT query and return rows as dictionaries."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, args)
            results = cur.fetchall()
            return (results[0] if results else None) if one else results
    finally:
        conn.close()

def execute_db(query, args=(), return_id=False):
    """Execute an INSERT, UPDATE, or DELETE query and commit transaction."""
    conn = get_db_connection()
    try:
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

