"""
Setup script - installs MySQL, creates DB and tables, seeds sample data.
Run this ONCE before starting the app.
"""
import subprocess
import sys
import os
import time

def check_mysql_running():
    import pymysql
    try:
        conn = pymysql.connect(host='localhost', user='root', password='', port=3306, connect_timeout=5)
        conn.close()
        return True
    except:
        return False

def setup_database():
    import pymysql
    print("\n[2/3] Setting up database...")

    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    schema_file = os.path.join(db_dir, 'schema.sql')
    seed_file = os.path.join(db_dir, 'seed_data.py')

    # Read schema SQL
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn = pymysql.connect(host='localhost', user='root', password='', port=3306, charset='utf8mb4')
    with conn.cursor() as cur:
        # Execute each statement
        for statement in schema_sql.split(';'):
            stmt = statement.strip()
            if stmt and not stmt.startswith('--'):
                try:
                    cur.execute(stmt)
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        print(f"  Warning: {e}")
        conn.commit()
    conn.close()
    print("  ✅ Schema created successfully!")

    # Run seed data
    if os.path.exists(seed_file):
        print("  Seeding sample data...")
        result = subprocess.run([sys.executable, seed_file], capture_output=True, text=True, 
                                cwd=os.path.dirname(__file__))
        if result.returncode == 0:
            print("  ✅ Sample data seeded!")
        else:
            print(f"  ⚠️  Seed warning: {result.stderr[:200]}")

def main():
    print("=" * 55)
    print("  Job Portal for Freshers - Setup Script")
    print("=" * 55)

    # Step 1: Check MySQL
    print("\n[1/3] Checking MySQL connection...")
    if check_mysql_running():
        print("  ✅ MySQL is running!")
    else:
        print("  ❌ MySQL is NOT running!")
        print("\n  Please install and start MySQL:")
        print("  1. Download: https://dev.mysql.com/downloads/installer/")
        print("  2. Install with root password = (empty/blank)")
        print("  3. Start MySQL service")
        print("  4. Run this script again")
        sys.exit(1)

    # Step 2: Setup DB
    setup_database()

    # Step 3: Done
    print("\n[3/3] All done!")
    print("\n  ✅ Setup complete! Now run the app with:")
    print("     python app.py")
    print("\n  Then open: http://localhost:5000")
    print("=" * 55)

if __name__ == '__main__':
    main()

