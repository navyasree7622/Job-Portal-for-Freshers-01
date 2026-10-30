import os
import pymysql
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta

def seed_database(conn=None, is_sqlite=False):
    close_at_end = False
    if conn is None:
        try:
            host = os.getenv('MYSQL_HOST', 'localhost')
            user = os.getenv('MYSQL_USER', 'root')
            password = os.getenv('MYSQL_PASSWORD', '')
            database = os.getenv('MYSQL_DB', 'job_portal_db')
            port = int(os.getenv('MYSQL_PORT', 3306))
            conn = pymysql.connect(
                host=host, user=user, password=password, database=database,
                port=port, cursorclass=pymysql.cursors.DictCursor, autocommit=False, connect_timeout=1
            )
            is_sqlite = False
            close_at_end = True
        except Exception:
            import sqlite3
            sqlite_path = os.path.join(os.path.dirname(__file__), 'job_portal.db')
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            conn.create_function("NOW", 0, lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            is_sqlite = True
            close_at_end = True

    def q(sql):
        return sql.replace('%s', '?') if is_sqlite else sql

    try:
        cur = conn.cursor()
        if True:
            # Disable foreign key checks for clean truncation and population
            if is_sqlite:
                cur.execute("PRAGMA foreign_keys = OFF;")
                for t in ['audit_logs', 'reports', 'notifications', 'saved_jobs', 'applications', 'jobs', 'companies', 'fresher_profiles', 'users']:
                    cur.execute(f"DELETE FROM {t};")
                cur.execute("PRAGMA foreign_keys = ON;")
            else:
                cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
                for t in ['audit_logs', 'reports', 'notifications', 'saved_jobs', 'applications', 'jobs', 'companies', 'fresher_profiles', 'users']:
                    cur.execute(f"TRUNCATE TABLE {t};")
                cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

            print("Truncated tables. Seeding rich recruitment dataset...")

            # 1. Users (Admin, Recruiters, Freshers)
            users_data = [
                # Admin
                ('Platform Admin', 'admin@firststep.com', generate_password_hash('admin123'), 'admin', 1),
                
                # Recruiters
                ('Priya Nair (TCS)', 'tcs.careers@tcs.com', generate_password_hash('recruiter123'), 'recruiter', 1),
                ('Rajesh Verma (Infosys)', 'careers@infosys.com', generate_password_hash('recruiter123'), 'recruiter', 1),
                ('Sneha Kulkarni (Wipro)', 'hiring@wipro.com', generate_password_hash('recruiter123'), 'recruiter', 1),
                ('Arun Kumar (Zoho)', 'jobs@zoho.com', generate_password_hash('recruiter123'), 'recruiter', 1),
                ('Meera Sen (Cognizant)', 'talent@cognizant.com', generate_password_hash('recruiter123'), 'recruiter', 1),
                ('Vikram Singhania (HCL)', 'recruitment@hcl.com', generate_password_hash('recruiter123'), 'recruiter', 1),
                ('Aditi Sharma (Capgemini)', 'campus@capgemini.com', generate_password_hash('recruiter123'), 'recruiter', 1),
                
                # Freshers
                ('Rahul Sharma', 'rahul.sharma@gmail.com', generate_password_hash('fresher123'), 'fresher', 1),
                ('Ananya Patel', 'ananya.patel@gmail.com', generate_password_hash('fresher123'), 'fresher', 1),
                ('Vikram Aditya', 'vikram.aditya@gmail.com', generate_password_hash('fresher123'), 'fresher', 1),
                ('Divya Iyer', 'divya.iyer@gmail.com', generate_password_hash('fresher123'), 'fresher', 1),
                ('Siddharth Rao', 'siddharth.rao@gmail.com', generate_password_hash('fresher123'), 'fresher', 1),
                ('Pooja Hegde', 'pooja.hegde@gmail.com', generate_password_hash('fresher123'), 'fresher', 1)
            ]

            insert_user_sql = """
                INSERT INTO users (name, email, password_hash, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cur.executemany(q(insert_user_sql), users_data)

            cur.execute("SELECT id, email FROM users")
            user_map = {row['email']: row['id'] for row in cur.fetchall()}

            # 2. Fresher Profiles
            fresher_profiles = [
                (
                    user_map['rahul.sharma@gmail.com'],
                    '+91 98765 43210',
                    'Bangalore, Karnataka',
                    'B.Tech / B.E.',
                    'Computer Science & Engineering',
                    'National Institute of Technology Karnataka (NITK)',
                    2026,
                    '8.7 CGPA',
                    'Python, Flask, JavaScript, React, SQL, Git, REST APIs, HTML/CSS',
                    'Fresher (0-1 yr)',
                    'Driven computer science graduate with solid full-stack project experience, algorithmic problem-solving skills, and a passion for backend web services.',
                    'https://github.com/rahul-sharma',
                    'https://linkedin.com/in/rahul-sharma-dev',
                    'https://rahulsharma.dev',
                    'sample_resume_rahul.pdf',
                    'Rahul_Sharma_BTech_Resume.pdf'
                ),
                (
                    user_map['ananya.patel@gmail.com'],
                    '+91 98111 22334',
                    'Hyderabad, Telangana',
                    'BCA',
                    'Computer Applications & Software Engineering',
                    'St. Joseph College of Information Science',
                    2026,
                    '8.9 CGPA',
                    'Java, Spring Boot, MySQL, OOP, Data Structures, Postman, Git',
                    'Fresher (0-1 yr)',
                    'Passionate Java developer with hands-on coursework in Spring microservices, relational database tuning, and API design.',
                    'https://github.com/ananya-patel',
                    'https://linkedin.com/in/ananya-patel-tech',
                    'https://ananyapatel.me',
                    'sample_resume_ananya.pdf',
                    'Ananya_Patel_Java_Resume.pdf'
                ),
                (
                    user_map['vikram.aditya@gmail.com'],
                    '+91 97222 33445',
                    'Pune, Maharashtra',
                    'B.Sc',
                    'Data Science & Statistics',
                    'Savitribai Phule Pune University',
                    2026,
                    '8.4 CGPA',
                    'Python, SQL, Pandas, NumPy, Scikit-Learn, Power BI, Statistics, Tableau',
                    'Fresher (0-1 yr)',
                    'Analytical fresher specializing in predictive data modeling, statistical hypothesis testing, and dashboard design for business intelligence.',
                    'https://github.com/vikram-aditya',
                    'https://linkedin.com/in/vikram-aditya-data',
                    'https://vikramaditya.portfolio',
                    'sample_resume_vikram.pdf',
                    'Vikram_Aditya_DataAnalyst_Resume.pdf'
                ),
                (
                    user_map['divya.iyer@gmail.com'],
                    '+91 96333 44556',
                    'Chennai, Tamil Nadu',
                    'B.Tech / B.E.',
                    'Information Technology & Multimedia',
                    'Anna University College of Engineering',
                    2026,
                    '8.6 CGPA',
                    'Figma, UI/UX Design, Wireframing, User Research, Prototyping, HTML5, CSS3',
                    'Fresher (0-1 yr)',
                    'Human-centric UI/UX designer blending qualitative user research with polished Figma component libraries and responsive front-end prototypes.',
                    'https://github.com/divya-iyer',
                    'https://linkedin.com/in/divya-iyer-design',
                    'https://behance.net/divyaiyer',
                    'sample_resume_divya.pdf',
                    'Divya_Iyer_UIUX_Resume.pdf'
                ),
                (
                    user_map['siddharth.rao@gmail.com'],
                    '+91 95444 55667',
                    'Gurgaon, Haryana',
                    'B.Tech / B.E.',
                    'Electronics & Communication Engineering',
                    'Delhi Technological University (DTU)',
                    2026,
                    '8.2 CGPA',
                    'Linux, AWS Basics, Docker, Python, Bash, TCP/IP, Git, CI/CD',
                    'Fresher (0-1 yr)',
                    'Cloud and infrastructure enthusiast eager to start as a Cloud Support Associate or Junior DevOps trainee.',
                    'https://github.com/siddharth-rao',
                    'https://linkedin.com/in/siddharth-rao-cloud',
                    'https://siddharth.dev',
                    'sample_resume_rahul.pdf',
                    'Siddharth_Rao_DevOps_Resume.pdf'
                ),
                (
                    user_map['pooja.hegde@gmail.com'],
                    '+91 94555 66778',
                    'Bangalore, Karnataka',
                    'BBA / MBA',
                    'Marketing & Business Analytics',
                    'Christ University Bangalore',
                    2026,
                    '8.8 CGPA',
                    'Business Analysis, SQL Basics, Excel Modeling, Digital Marketing, Market Research, Communication',
                    'Fresher (0-1 yr)',
                    'Business and product analyst intern ready to assist cross-functional product and growth teams with data-backed insights.',
                    'https://github.com/pooja-hegde',
                    'https://linkedin.com/in/pooja-hegde-biz',
                    'https://poojahegde.com',
                    'sample_resume_ananya.pdf',
                    'Pooja_Hegde_BusinessAnalyst_Resume.pdf'
                )
            ]

            insert_profile_sql = """
                INSERT INTO fresher_profiles (
                    user_id, phone, location, education, degree, institution,
                    graduation_year, cgpa, skills, experience_level, bio,
                    github_url, linkedin_url, portfolio_url, resume_path, resume_filename
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.executemany(q(insert_profile_sql), fresher_profiles)

            # 3. Companies
            companies_data = [
                (
                    user_map['tcs.careers@tcs.com'],
                    'Tata Consultancy Services (TCS)',
                    'IT Services & Consulting',
                    'TCS is a global leader in IT consulting and digital transformation, actively recruiting graduating engineering talent for premier Trainee and Digital cohorts.',
                    'Bangalore, Karnataka',
                    'https://www.tcs.com',
                    'careers@tcs.com',
                    'verified'
                ),
                (
                    user_map['careers@infosys.com'],
                    'Infosys Technologies',
                    'Enterprise Software & Digital Services',
                    'Infosys is a global enterprise solutions provider renowned for its world-class fresher foundation training program at the Mysore Global Education Center.',
                    'Hyderabad, Telangana',
                    'https://www.infosys.com',
                    'careers@infosys.com',
                    'verified'
                ),
                (
                    user_map['hiring@wipro.com'],
                    'Wipro Digital',
                    'Cloud, Security & IT Engineering',
                    'Wipro drives cloud modernization, hyper-automation, and next-gen software engineering with early career acceleration paths for college freshers.',
                    'Pune, Maharashtra',
                    'https://www.wipro.com',
                    'hiring@wipro.com',
                    'verified'
                ),
                (
                    user_map['jobs@zoho.com'],
                    'Zoho Corporation',
                    'SaaS & Enterprise Cloud',
                    'Zoho builds award-winning cloud applications used by over 100 million users worldwide, prioritizing problem-solving curiosity and hands-on craftsmanship.',
                    'Chennai, Tamil Nadu',
                    'https://www.zoho.com',
                    'jobs@zoho.com',
                    'verified'
                ),
                (
                    user_map['talent@cognizant.com'],
                    'Cognizant Technology Solutions',
                    'Technology & Cloud Solutions',
                    'Cognizant engineers intelligent digital platforms, modern cloud architectures, and customer-first software for leading global enterprises.',
                    'Gurgaon, Haryana',
                    'https://www.cognizant.com',
                    'talent@cognizant.com',
                    'verified'
                ),
                (
                    user_map['recruitment@hcl.com'],
                    'HCL Tech',
                    'Engineering & Cloud Services',
                    'HCL Tech supercharges progression with deep engineering expertise, digital consulting, and premier graduate trainee incubation centers.',
                    'Noida, Uttar Pradesh',
                    'https://www.hcltech.com',
                    'recruitment@hcl.com',
                    'verified'
                ),
                (
                    user_map['campus@capgemini.com'],
                    'Capgemini India',
                    'Digital Consulting & Engineering',
                    'Capgemini guides global brands through digital transformation, cloud migrations, and agile software development across India.',
                    'Mumbai, Maharashtra',
                    'https://www.capgemini.com',
                    'campus@capgemini.com',
                    'pending'
                )
            ]

            insert_company_sql = """
                INSERT INTO companies (
                    recruiter_user_id, company_name, industry, description,
                    location, website, contact_email, verification_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.executemany(q(insert_company_sql), companies_data)

            cur.execute("SELECT id, recruiter_user_id, company_name FROM companies")
            comp_rows = cur.fetchall()
            comp_map = {row['company_name']: (row['id'], row['recruiter_user_id']) for row in comp_rows}

            # 4. Jobs across all required categories (40+ listings)
            d_future = date.today() + timedelta(days=45)
            d_soon = date.today() + timedelta(days=15)
            d_nextweek = date.today() + timedelta(days=7)

            jobs_data = [
                # ---------------- SOFTWARE DEVELOPMENT (10 roles) ----------------
                (
                    comp_map['Tata Consultancy Services (TCS)'][0], comp_map['Tata Consultancy Services (TCS)'][1],
                    'Junior Software Developer (Python & SQL)', 'Software Development',
                    'Join the TCS engineering team as a Junior Software Developer. You will contribute to modular backend services, database schema design, and unit test automation.',
                    '- Develop clean, testable backend code in Python.\n- Implement relational database queries and performance indexes.\n- Participate in daily standups and code reviews.',
                    'Python, SQL, Git, OOP, Data Structures, REST APIs',
                    'B.Tech / B.E. / MCA / B.Sc in CS or IT (2025/2026 Batch). Minimum 60% aggregate.',
                    'Bangalore, Karnataka', 'Full-Time', 'Hybrid', 'Fresher (0-1 yr)',
                    450000, 650000, d_future, 'published', 1, 1, 142
                ),
                (
                    comp_map['Infosys Technologies'][0], comp_map['Infosys Technologies'][1],
                    'Python Developer Intern (Paid 6-Month Fast-Track)', 'Software Development',
                    'Full-time conversion opportunity upon completion. Work with senior architects developing scalable RESTful microservices and data ingestion pipelines.',
                    '- Build API endpoints using Python Flask/FastAPI.\n- Write unit tests and maintain API documentation.\n- Integrate third-party web services.',
                    'Python, Flask, REST APIs, JSON, Git, Postman',
                    'Final year students or recent freshers graduating in 2026.',
                    'Remote', 'Internship', 'Remote', 'Fresher (0-1 yr)',
                    300000, 380000, d_soon, 'published', 1, 1, 210
                ),
                (
                    comp_map['Infosys Technologies'][0], comp_map['Infosys Technologies'][1],
                    'Java Developer Trainee (Spring Boot)', 'Software Development',
                    'Undergo comprehensive foundation training at the Infosys Mysore campus followed by deployment onto enterprise banking and commerce projects.',
                    '- Implement object-oriented business logic in Java 17.\n- Build REST microservices with Spring Boot and Spring Data JPA.\n- Collaborate in Agile sprint deliveries.',
                    'Java, Spring Boot, MySQL, OOP, Data Structures, Git',
                    'B.Tech / B.E. / BCA / MCA. Solid foundation in core Java.',
                    'Hyderabad, Telangana', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    420000, 560000, d_future, 'published', 1, 1, 175
                ),
                (
                    comp_map['Wipro Digital'][0], comp_map['Wipro Digital'][1],
                    'Junior Full Stack Developer (React & Node.js)', 'Software Development',
                    'Design responsive web applications and scalable API layers for international healthcare and telecom clients.',
                    '- Build interactive components with modern React and CSS3.\n- Connect frontends to Node.js / Express microservices.\n- Ensure mobile responsiveness and cross-browser fidelity.',
                    'React, JavaScript (ES6+), Node.js, HTML5, CSS3, SQL',
                    'Graduates in Computer Science, IT, or BCA. Portfolio or GitHub projects required.',
                    'Pune, Maharashtra', 'Full-Time', 'Hybrid', 'Fresher (0-1 yr)',
                    450000, 600000, d_future, 'published', 0, 1, 130
                ),
                (
                    comp_map['Zoho Corporation'][0], comp_map['Zoho Corporation'][1],
                    'Frontend Developer Intern', 'Software Development',
                    'Work closely with Zoho design and product teams to craft fast, responsive, and accessible user interfaces for SaaS web applications.',
                    '- Convert Figma specifications into semantic HTML, CSS, and modern JavaScript.\n- Optimize web assets and reduce page load latency.\n- Test browser compatibility.',
                    'HTML5, CSS3, JavaScript, Responsive Design, Git',
                    'Any degree with strong demonstrated frontend coding skills.',
                    'Chennai, Tamil Nadu', 'Internship', 'Onsite', 'Fresher (0-1 yr)',
                    280000, 360000, d_soon, 'published', 1, 1, 195
                ),
                (
                    comp_map['HCL Tech'][0], comp_map['HCL Tech'][1],
                    'Backend Developer Trainee (Node.js & Python)', 'Software Development',
                    'Learn server-side application development, caching strategies, and database optimization techniques under experienced engineering mentors.',
                    '- Write scalable server-side handlers and database queries.\n- Debug performance bottlenecks in web applications.\n- Participate in peer review sessions.',
                    'Python, Node.js, SQL, Express, REST APIs',
                    'B.Tech, B.E., MCA 2025/2026 Batch.',
                    'Noida, Uttar Pradesh', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    400000, 520000, d_future, 'published', 0, 1, 88
                ),
                (
                    comp_map['Cognizant Technology Solutions'][0], comp_map['Cognizant Technology Solutions'][1],
                    'Junior Web Developer (HTML, CSS & JavaScript)', 'Software Development',
                    'Maintain client portal websites, modernize user interfaces, and implement interactive client-side components.',
                    '- Develop modular UI components using CSS custom properties.\n- Write vanilla JavaScript DOM logic and form validation scripts.\n- Ensure high web accessibility standards.',
                    'HTML5, CSS3, JavaScript, Git, Web Accessibility',
                    'Graduates in any technical discipline with strong web design basics.',
                    'Gurgaon, Haryana', 'Full-Time', 'Hybrid', 'Fresher (0-1 yr)',
                    380000, 480000, d_future, 'published', 0, 1, 74
                ),
                (
                    comp_map['Wipro Digital'][0], comp_map['Wipro Digital'][1],
                    'React Developer Intern (Paid)', 'Software Development',
                    'Build high-performance single page web applications using React functional components, hooks, and clean state management.',
                    '- Create reusable React component libraries.\n- Consume RESTful API endpoints.\n- Write automated unit tests using Jest.',
                    'React, Redux/Context, JavaScript, CSS3, Git',
                    'Pre-final or final year students with working React demo apps.',
                    'Remote', 'Internship', 'Remote', 'Fresher (0-1 yr)',
                    320000, 400000, d_soon, 'published', 1, 1, 230
                ),
                (
                    comp_map['Zoho Corporation'][0], comp_map['Zoho Corporation'][1],
                    'Android Developer Intern (Kotlin)', 'Software Development',
                    'Contribute to mobile productivity apps with millions of active users. Write clean Kotlin code and learn native Android architecture patterns.',
                    '- Assist in developing Android UI screens using XML and Jetpack Compose.\n- Optimize local caching using Room database.\n- Test app on various screen sizes and Android versions.',
                    'Kotlin, Android SDK, Java, XML, Git',
                    'Enthusiastic mobile developers with personal Android apps or GitHub code.',
                    'Chennai, Tamil Nadu', 'Internship', 'Onsite', 'Fresher (0-1 yr)',
                    300000, 420000, d_soon, 'published', 0, 1, 160
                ),
                (
                    comp_map['Tata Consultancy Services (TCS)'][0], comp_map['Tata Consultancy Services (TCS)'][1],
                    'Associate Software Engineer (Core Systems)', 'Software Development',
                    'Work on resilient enterprise application logic, message queues, and cloud backend systems for Fortune 500 customers.',
                    '- Develop core software services complying with high reliability standards.\n- Write automated unit tests and benchmark throughput.\n- Support production deployment activities.',
                    'Java/C++, Python, SQL, Linux, Algorithms',
                    'B.Tech / B.E. in CS, ECE, IT with 65%+ throughout academics.',
                    'Bangalore, Karnataka', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    480000, 700000, d_future, 'published', 1, 1, 280
                ),

                # ---------------- DATA AND ARTIFICIAL INTELLIGENCE (8 roles) ----------------
                (
                    comp_map['Tata Consultancy Services (TCS)'][0], comp_map['Tata Consultancy Services (TCS)'][1],
                    'Data Analyst Intern (Paid)', 'Data & Analytics',
                    'Process, clean, and model complex transactional datasets to deliver business dashboards and exploratory analytics.',
                    '- Write analytical SQL queries to extract data from data warehouses.\n- Build visual charts and dashboards in Power BI.\n- Clean messy datasets using Python Pandas.',
                    'SQL, Python, Pandas, Excel, Power BI, Statistics',
                    'Degrees in Data Science, Statistics, Mathematics, CS or Engineering.',
                    'Bangalore, Karnataka', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    320000, 400000, d_soon, 'published', 1, 1, 245
                ),
                (
                    comp_map['Infosys Technologies'][0], comp_map['Infosys Technologies'][1],
                    'Junior Data Analyst', 'Data & Analytics',
                    'Collaborate with analytics consultants to convert raw business data into actionable executive reports and KPIs.',
                    '- Formulate SQL aggregations, window functions, and joins.\n- Automate routine weekly and monthly reporting spreadsheets.\n- Present findings to business teams.',
                    'SQL, Python, Power BI, Tableau, Advanced Excel',
                    'Graduates in Statistics, Computer Science, Economics or Engineering.',
                    'Hyderabad, Telangana', 'Full-Time', 'Hybrid', 'Fresher (0-1 yr)',
                    420000, 580000, d_future, 'published', 1, 1, 165
                ),
                (
                    comp_map['Wipro Digital'][0], comp_map['Wipro Digital'][1],
                    'SQL Developer Trainee', 'Data & Analytics',
                    'Design and optimize relational database schemas, write stored procedures, views, and automated ETL data transformation pipelines.',
                    '- Write performant SQL queries, indexes, and constraints.\n- Monitor database query execution plans.\n- Ensure data integrity and regular database backups.',
                    'SQL, MySQL/PostgreSQL, Database Design, Stored Procedures, ETL',
                    'BCA, B.Sc, B.Tech graduates with strong relational database concepts.',
                    'Pune, Maharashtra', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    380000, 500000, d_future, 'published', 0, 1, 95
                ),
                (
                    comp_map['HCL Tech'][0], comp_map['HCL Tech'][1],
                    'Data Science Intern', 'Data & Analytics',
                    'Explore statistical machine learning algorithms on real-world datasets, build predictive regression/classification models, and evaluate precision/recall metrics.',
                    '- Conduct exploratory data analysis (EDA) in Jupyter Notebooks.\n- Engineer features from structured and unstructured records.\n- Train baseline scikit-learn models.',
                    'Python, Pandas, NumPy, Scikit-Learn, Statistics, Matplotlib',
                    'Students or graduates in CS, Data Science, AI or Applied Math.',
                    'Noida, Uttar Pradesh', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    350000, 450000, d_soon, 'published', 1, 1, 310
                ),
                (
                    comp_map['Cognizant Technology Solutions'][0], comp_map['Cognizant Technology Solutions'][1],
                    'Machine Learning Intern', 'Data & Analytics',
                    'Assist in developing and deploying supervised and unsupervised machine learning models for customer segmentation and forecasting.',
                    '- Preprocess training data and handle missing values.\n- Run model evaluations and hyperparameter sweeps.\n- Package models as REST API inference endpoints.',
                    'Python, Scikit-Learn, TensorFlow/PyTorch Basics, SQL, Git',
                    'Graduates with demonstrated coursework and projects in machine learning.',
                    'Gurgaon, Haryana', 'Internship', 'Remote', 'Fresher (0-1 yr)',
                    360000, 480000, d_soon, 'published', 1, 1, 280
                ),
                (
                    comp_map['Tata Consultancy Services (TCS)'][0], comp_map['Tata Consultancy Services (TCS)'][1],
                    'AI Engineer Intern (NLP & LLMs)', 'Data & Analytics',
                    'Experiment with natural language processing, embeddings, vector databases, and prompt engineering pipelines.',
                    '- Implement text classification and sentiment analysis pipelines.\n- Benchmark open-source language models.\n- Build internal workflow assistants.',
                    'Python, NLP, HuggingFace, LangChain Basics, Vector DBs, REST APIs',
                    'B.Tech / M.Tech in CS or Data Science.',
                    'Bangalore, Karnataka', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    380000, 500000, d_nextweek, 'published', 1, 1, 340
                ),
                (
                    comp_map['Capgemini India'][0], comp_map['Capgemini India'][1],
                    'Business Intelligence Intern (Power BI & Tableau)', 'Data & Analytics',
                    'Create interactive dashboards, automated KPI monitors, and data visualizations for retail and supply chain stakeholders.',
                    '- Transform datasets using Power Query.\n- Write DAX measures and calculated columns.\n- Design visual dashboards following corporate branding guidelines.',
                    'Power BI, DAX, SQL, Tableau, Excel, Data Modeling',
                    'Graduates in Business, Engineering or Mathematics.',
                    'Mumbai, Maharashtra', 'Internship', 'Onsite', 'Fresher (0-1 yr)',
                    300000, 400000, d_soon, 'published', 0, 1, 115
                ),
                (
                    comp_map['Infosys Technologies'][0], comp_map['Infosys Technologies'][1],
                    'Junior Database Developer (MySQL & PostgreSQL)', 'Data & Analytics',
                    'Maintain database reliability, write complex analytical triggers, optimize index strategies, and perform database migrations.',
                    '- Develop normalized tables, constraints, and stored procedures.\n- Analyze slow query logs and optimize indexes.\n- Document database dictionary schemas.',
                    'MySQL, PostgreSQL, SQL, Database Normalization, Performance Tuning',
                    'B.Tech / BCA / B.Sc in IT or Computer Science.',
                    'Hyderabad, Telangana', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    400000, 540000, d_future, 'published', 0, 1, 85
                ),

                # ---------------- TESTING AND CYBERSECURITY (6 roles) ----------------
                (
                    comp_map['Zoho Corporation'][0], comp_map['Zoho Corporation'][1],
                    'Software Testing Intern', 'Quality Assurance',
                    'Learn the complete software test lifecycle. Write comprehensive test cases, perform regression testing, and verify user experience flows.',
                    '- Create detailed test scenarios from product specifications.\n- Log defects with reproduction steps and screenshots.\n- Verify bug fixes and perform regression tests.',
                    'Manual Testing, Test Cases, Bug Reporting, Jira Basics, Web Testing',
                    'Any graduate with strong attention to detail and analytical mindset.',
                    'Chennai, Tamil Nadu', 'Internship', 'Onsite', 'Fresher (0-1 yr)',
                    260000, 340000, d_soon, 'published', 0, 1, 120
                ),
                (
                    comp_map['Wipro Digital'][0], comp_map['Wipro Digital'][1],
                    'Manual Testing Trainee', 'Quality Assurance',
                    'Perform exploratory and boundary value testing across responsive web and mobile application builds.',
                    '- Validate form inputs, security checks, and cross-browser layouts.\n- Collaborate with developers to clarify edge cases.\n- Document test summary reports.',
                    'Manual QA, STLC, SDLC, Test Execution, Bug Tracking',
                    'B.Sc, BCA, B.Tech graduates.',
                    'Pune, Maharashtra', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    350000, 450000, d_future, 'published', 0, 1, 78
                ),
                (
                    comp_map['Infosys Technologies'][0], comp_map['Infosys Technologies'][1],
                    'Automation Testing Intern (Selenium & Python)', 'Quality Assurance',
                    'Build automated regression test suites using Selenium WebDriver and Python. Execute automated browser tests in CI/CD pipelines.',
                    '- Write automated web test scripts in Python with PyTest.\n- Implement Page Object Model (POM) architecture.\n- Automate API verification with Postman/Requests.',
                    'Selenium, Python, PyTest, XPath, Git, Postman',
                    'Graduates with basic Python coding and QA enthusiasm.',
                    'Hyderabad, Telangana', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    320000, 420000, d_soon, 'published', 1, 1, 180
                ),
                (
                    comp_map['HCL Tech'][0], comp_map['HCL Tech'][1],
                    'QA Engineer Trainee (Web & API Testing)', 'Quality Assurance',
                    'Ensure top-tier quality for enterprise software releases. Test REST API endpoints, security authentication tokens, and web performance.',
                    '- Design test plans for newly implemented REST endpoints.\n- Verify JSON schema payloads and status codes.\n- Automate regression test suites.',
                    'API Testing, Postman, SQL, Selenium Basics, Manual QA',
                    'B.Tech / B.E. / MCA in Computer Science or IT.',
                    'Noida, Uttar Pradesh', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    380000, 500000, d_future, 'published', 0, 1, 92
                ),
                (
                    comp_map['Cognizant Technology Solutions'][0], comp_map['Cognizant Technology Solutions'][1],
                    'Cybersecurity Intern (SOC & Network Security)', 'Security',
                    'Gain practical experience in a modern security operations center (SOC). Monitor security alerts, analyze log events, and run vulnerability scans.',
                    '- Triaging security incidents and anomalous network traffic.\n- Run automated vulnerability assessments.\n- Document findings and remediations.',
                    'Networking (TCP/IP), Linux, Cybersecurity Fundamentals, SIEM Basics, Python',
                    'Graduates in CS, IT, Cybersecurity or Electronics.',
                    'Gurgaon, Haryana', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    360000, 480000, d_soon, 'published', 1, 1, 260
                ),
                (
                    comp_map['Tata Consultancy Services (TCS)'][0], comp_map['Tata Consultancy Services (TCS)'][1],
                    'Information Security Analyst Trainee', 'Security',
                    'Participate in enterprise security compliance audits, vulnerability management, and employee security training programs.',
                    '- Assist in assessing security policy compliance.\n- Review system patch status across corporate servers.\n- Support penetration testing teams with report formatting.',
                    'Network Security, OS Hardening, Identity Access Management (IAM), Linux, Python',
                    'B.Tech / B.E. in Computer Science or Information Security.',
                    'Bangalore, Karnataka', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    450000, 620000, d_future, 'published', 1, 1, 150
                ),

                # ---------------- CLOUD AND IT (6 roles) ----------------
                (
                    comp_map['Infosys Technologies'][0], comp_map['Infosys Technologies'][1],
                    'Cloud Support Associate (AWS & Azure)', 'Cloud & DevOps',
                    'Assist global enterprise clients with cloud server provisioning, storage configuration, networking rules, and uptime monitoring.',
                    '- Monitor server health and cloud metrics in AWS CloudWatch / Azure Monitor.\n- Troubleshoot DNS, SSL, and network firewall configuration issues.\n- Automate recurring administrative tasks.',
                    'AWS/Azure Basics, Linux, Networking (DNS, TCP/IP, SSH), Python/Bash',
                    'B.Tech/B.E in CS, ECE, IT. Cloud certifications are a bonus.',
                    'Bangalore, Karnataka', 'Full-Time', 'Hybrid', 'Fresher (0-1 yr)',
                    420000, 580000, d_future, 'published', 1, 1, 190
                ),
                (
                    comp_map['Wipro Digital'][0], comp_map['Wipro Digital'][1],
                    'DevOps Intern (Docker & CI/CD)', 'Cloud & DevOps',
                    'Learn continuous integration and continuous deployment (CI/CD) pipelines, Docker containerization, and automated build scripts.',
                    '- Write Dockerfiles and configure multi-stage container builds.\n- Assist in configuring GitHub Actions and Jenkins pipelines.\n- Document deployment procedures.',
                    'Docker, Linux, Git, GitHub Actions, Bash, Python',
                    'Final-year students with a passion for software delivery automation.',
                    'Pune, Maharashtra', 'Internship', 'Remote', 'Fresher (0-1 yr)',
                    340000, 440000, d_soon, 'published', 1, 1, 220
                ),
                (
                    comp_map['HCL Tech'][0], comp_map['HCL Tech'][1],
                    'Technical Support Engineer (L1)', 'Cloud & DevOps',
                    'Provide frontline technical support to business software users. Investigate software errors, query relational databases, and log bug tickets.',
                    '- Investigate user reported application errors.\n- Query MySQL databases to diagnose transaction discrepancies.\n- Coordinate with engineering teams to deploy bug fixes.',
                    'SQL Basics, Troubleshooting, Communication, Windows/Linux OS, Ticketing Tools',
                    'Any graduate (B.Sc, BCA, B.Tech, B.Com) with good problem-solving ability.',
                    'Noida, Uttar Pradesh', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    340000, 460000, d_future, 'published', 0, 1, 65
                ),
                (
                    comp_map['Cognizant Technology Solutions'][0], comp_map['Cognizant Technology Solutions'][1],
                    'IT Support Trainee (Enterprise Systems)', 'Cloud & DevOps',
                    'Manage employee hardware, software licenses, VPN configurations, and domain user accounts in an active directory environment.',
                    '- Configure operating system images and user permissions.\n- Support remote employees with VPN and software installation issues.\n- Maintain hardware inventory records.',
                    'Hardware & Networking, Windows 11, Active Directory, Troubleshooting',
                    'Diploma in IT/CS or Graduates in any discipline.',
                    'Gurgaon, Haryana', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    320000, 420000, d_future, 'published', 0, 1, 50
                ),
                (
                    comp_map['Tata Consultancy Services (TCS)'][0], comp_map['Tata Consultancy Services (TCS)'][1],
                    'Network Engineer Trainee', 'Cloud & DevOps',
                    'Work on enterprise campus network infrastructure, switch routing, VLANs, Wi-Fi access points, and firewall policies.',
                    '- Configure network switches and routers following engineering blueprints.\n- Monitor bandwidth consumption and latency bottlenecks.\n- Assist in cable patching and rack maintenance.',
                    'CCNA Fundamentals, Routing & Switching, Subnetting, TCP/IP, Wireshark',
                    'B.Tech / B.E. in Electronics, Telecommunication, or Computer Science.',
                    'Bangalore, Karnataka', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    400000, 520000, d_future, 'published', 0, 1, 85
                ),
                (
                    comp_map['Capgemini India'][0], comp_map['Capgemini India'][1],
                    'Cloud Engineering Intern (Google Cloud Platform)', 'Cloud & DevOps',
                    'Hands-on internship deploying serverless functions, cloud storage buckets, and microservice containers on GCP.',
                    '- Set up GCP cloud resources using the Google Cloud Console and CLI.\n- Write lightweight Python cloud functions.\n- Monitor serverless log metrics.',
                    'GCP / AWS Basics, Python, Cloud Storage, Compute Engine, Networking',
                    'Pre-final or graduating students in CS or IT.',
                    'Mumbai, Maharashtra', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    320000, 420000, d_soon, 'published', 0, 1, 140
                ),

                # ---------------- BUSINESS AND DESIGN (8 roles) ----------------
                (
                    comp_map['Tata Consultancy Services (TCS)'][0], comp_map['Tata Consultancy Services (TCS)'][1],
                    'Business Analyst Intern', 'Business & Operations',
                    'Partner with business leaders and engineering squads to document software requirements, user stories, and process flowcharts.',
                    '- Interview business stakeholders to identify technical requirements.\n- Draft user stories with clear acceptance criteria in Jira.\n- Create process flow diagrams in Lucidchart/Visio.',
                    'Business Analysis, Requirement Gathering, Agile, User Stories, Excel, UML',
                    'B.Tech, BBA, MBA, or BCA graduates with strong communication.',
                    'Bangalore, Karnataka', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    350000, 450000, d_soon, 'published', 1, 1, 175
                ),
                (
                    comp_map['Zoho Corporation'][0], comp_map['Zoho Corporation'][1],
                    'UI/UX Design Intern', 'Design',
                    'Join the design lab at Zoho. Design user journeys, high-fidelity wireframes, responsive mobile prototypes, and design system components in Figma.',
                    '- Conduct usability audits of existing software workflows.\n- Create component variants and responsive auto-layouts in Figma.\n- Hand off pixel-perfect design specs to frontend engineers.',
                    'Figma, Wireframing, UX Research, Prototyping, Design Systems, HTML/CSS Basics',
                    'Any degree with an impressive UI/UX portfolio (Behance, Dribbble, or Website).',
                    'Chennai, Tamil Nadu', 'Internship', 'Onsite', 'Fresher (0-1 yr)',
                    360000, 500000, d_future, 'published', 1, 1, 260
                ),
                (
                    comp_map['Wipro Digital'][0], comp_map['Wipro Digital'][1],
                    'Digital Marketing Intern', 'Business & Operations',
                    'Execute search engine optimization (SEO), social media campaigns, blog distribution, and web traffic reporting.',
                    '- Conduct keyword research and optimize website metadata.\n- Create engaging social media graphics and LinkedIn campaign posts.\n- Track Google Analytics visitor metrics.',
                    'SEO, Content Writing, Google Analytics, Social Media Marketing, Canva',
                    'Graduates in Marketing, Mass Communication, or Business.',
                    'Pune, Maharashtra', 'Internship', 'Remote', 'Fresher (0-1 yr)',
                    250000, 350000, d_soon, 'published', 0, 1, 110
                ),
                (
                    comp_map['Zoho Corporation'][0], comp_map['Zoho Corporation'][1],
                    'Technical Content Writer (Software Documentation)', 'Business & Operations',
                    'Translate complex software features into lucid, easy-to-understand developer tutorials, API documentation, and help center guides.',
                    '- Write step-by-step guides for developer tools and cloud apps.\n- Test API endpoints and document code samples in Python/JavaScript.\n- Edit technical release notes.',
                    'Technical Writing, API Documentation, Markdown, Communication, Tech Curiosity',
                    'Graduates in English, Journalism, CS, or any field with flawless written English.',
                    'Chennai, Tamil Nadu', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    380000, 520000, d_future, 'published', 0, 1, 85
                ),
                (
                    comp_map['Infosys Technologies'][0], comp_map['Infosys Technologies'][1],
                    'Product Management Intern', 'Business & Operations',
                    'Shadow product managers during product discovery, competitive benchmarking, feature prioritization, and sprint planning.',
                    '- Analyze competitor product offerings and feature matrices.\n- Synthesize customer feedback into prioritized feature tickets.\n- Help run usability testing sessions.',
                    'Product Discovery, Market Research, Agile, Analytical Thinking, Communication',
                    'Pre-final or graduating students from top engineering or management colleges.',
                    'Hyderabad, Telangana', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    360000, 480000, d_soon, 'published', 1, 1, 215
                ),
                (
                    comp_map['Cognizant Technology Solutions'][0], comp_map['Cognizant Technology Solutions'][1],
                    'HR Recruiter Intern (Campus Hiring)', 'Business & Operations',
                    'Assist the campus recruitment team in screening resume submissions, scheduling technical interview slots, and coordinating college hiring drives.',
                    '- Screen candidate profiles against job eligibility checklists.\n- Coordinate interview schedules between recruiters and candidates.\n- Maintain applicant tracking system database records.',
                    'HR Screening, Communication, Interview Coordination, Excel, ATS Tools',
                    'Graduates in BBA, MBA (HR), Psychology, or Humanities.',
                    'Gurgaon, Haryana', 'Internship', 'Hybrid', 'Fresher (0-1 yr)',
                    280000, 360000, d_soon, 'published', 0, 1, 105
                ),
                (
                    comp_map['HCL Tech'][0], comp_map['HCL Tech'][1],
                    'Business Development Associate (Inside Sales Trainee)', 'Business & Operations',
                    'Identify and engage prospective corporate clients across North America and Europe for IT infrastructure and consulting solutions.',
                    '- Research target accounts on LinkedIn Sales Navigator.\n- Draft persuasive outbound email campaigns.\n- Qualify leads and arrange introductory meetings for sales managers.',
                    'Inside Sales, Lead Generation, Communication, CRM Basics, Market Research',
                    'Graduates in any stream with energetic verbal communication.',
                    'Noida, Uttar Pradesh', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    400000, 600000, d_future, 'published', 0, 1, 75
                ),
                (
                    comp_map['Zoho Corporation'][0], comp_map['Zoho Corporation'][1],
                    'Customer Success Associate (SaaS Applications)', 'Business & Operations',
                    'Help newly onboarded enterprise customers configure Zoho software, answer workflow questions, and drive product adoption.',
                    '- Conduct screen-share product onboarding walkthroughs.\n- Guide customers through settings, automations, and reporting widgets.\n- Advocate customer product improvement requests.',
                    'Customer Empathy, Active Listening, Problem Solving, Product Training, Written Communication',
                    'Any degree. Strong communication and patience are paramount.',
                    'Chennai, Tamil Nadu', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    380000, 520000, d_future, 'published', 0, 1, 95
                ),

                # ---------------- GRADUATE AND CORE ENGINEERING ROLES (4 roles) ----------------
                (
                    comp_map['Tata Consultancy Services (TCS)'][0], comp_map['Tata Consultancy Services (TCS)'][1],
                    'Graduate Engineer Trainee (GET - Electronics & Embedded)', 'Core Engineering',
                    'Join the embedded software and IoT practice. Develop firmware code, hardware interfacing drivers, and board diagnostics.',
                    '- Write embedded C/C++ firmware for microcontrollers.\n- Test communication protocols (UART, I2C, SPI, CAN).\n- Run circuit debugging using oscilloscopes and logic analyzers.',
                    'Embedded C, C++, Microcontrollers, Protocols (UART, SPI), Circuit Debugging',
                    'B.Tech / B.E. in Electronics & Communication, Electrical, or Instrumentation (2025/2026 Batch).',
                    'Bangalore, Karnataka', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    450000, 650000, d_future, 'published', 1, 1, 160
                ),
                (
                    comp_map['Capgemini India'][0], comp_map['Capgemini India'][1],
                    'Associate Engineer (Mechanical & CAD Design)', 'Core Engineering',
                    'Work with global automotive and aerospace engineering teams on 3D CAD modeling, component drafting, and tolerance simulations.',
                    '- Create parametric 3D models in CATIA / SolidWorks.\n- Generate 2D manufacturing engineering drawings.\n- Assist in design reviews and bill of materials (BOM) creation.',
                    'CAD (SolidWorks/CATIA), Engineering Drawing, GD&T, Material Science',
                    'B.Tech / B.E. in Mechanical, Automobile, or Aerospace Engineering.',
                    'Mumbai, Maharashtra', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    420000, 580000, d_future, 'published', 0, 1, 110
                ),
                (
                    comp_map['HCL Tech'][0], comp_map['HCL Tech'][1],
                    'Application Support Associate (Banking & Payments)', 'Core Engineering',
                    'Monitor and support high-availability online payment processing pipelines, transactional settlement systems, and API gateways.',
                    '- Monitor automated batch jobs and settlement queues.\n- Troubleshoot transaction drop-offs using SQL queries and log analyzers.\n- Escalate bugs to level-2 engineering teams.',
                    'SQL, Unix/Linux Commands, Transaction Flow, Problem Solving, Incident Management',
                    'B.Tech, B.Sc (IT), BCA graduates.',
                    'Noida, Uttar Pradesh', 'Full-Time', 'Hybrid', 'Fresher (0-1 yr)',
                    380000, 500000, d_future, 'published', 0, 1, 80
                ),
                (
                    comp_map['Infosys Technologies'][0], comp_map['Infosys Technologies'][1],
                    'Technical Operations Associate (Data Center & Cloud)', 'Core Engineering',
                    'Maintain 24x7 operational reliability across enterprise hybrid cloud data centers, virtual machine clusters, and backup storage pools.',
                    '- Perform routine system health checks and patch updates.\n- Respond to infrastructure monitoring alerts.\n- Execute verified operational runbooks and document incident resolutions.',
                    'Linux Administration Basics, Virtualization, Cloud Monitoring, Networking, Scripting',
                    'B.Tech / Diploma in CS, ECE, EE or Information Technology.',
                    'Hyderabad, Telangana', 'Full-Time', 'Onsite', 'Fresher (0-1 yr)',
                    400000, 520000, d_future, 'published', 0, 1, 70
                )
            ]

            insert_job_sql = """
                INSERT INTO jobs (
                    company_id, recruiter_user_id, title, category, description,
                    responsibilities, required_skills, eligibility, location,
                    job_type, work_arrangement, experience_level, salary_min, salary_max,
                    application_deadline, status, is_featured, is_sample, views_count, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cur.executemany(q(insert_job_sql), jobs_data)

            cur.execute("SELECT id, title FROM jobs")
            job_rows = cur.fetchall()
            job_map = {row['title']: row['id'] for row in job_rows}

            # 5. Sample Applications
            apps_data = [
                (
                    job_map['Junior Software Developer (Python & SQL)'],
                    user_map['rahul.sharma@gmail.com'],
                    'sample_resume_rahul.pdf',
                    'I have built full-stack Python web applications and feel confident about contributing to TCS backend engineering.',
                    'Under Review',
                    'Candidate has good problem-solving foundation. Profile forwarded to hiring manager.'
                ),
                (
                    job_map['Python Developer Intern (Paid 6-Month Fast-Track)'],
                    user_map['rahul.sharma@gmail.com'],
                    'sample_resume_rahul.pdf',
                    'Available full time for the 6-month internship. Strong proficiency with Flask, REST APIs, and SQL.',
                    'Interview Scheduled',
                    'Technical interview scheduled for Thursday 11:00 AM via video call.'
                ),
                (
                    job_map['Java Developer Trainee (Spring Boot)'],
                    user_map['ananya.patel@gmail.com'],
                    'sample_resume_ananya.pdf',
                    'Strong grasp of Java OOP and Spring Boot REST APIs with working academic microservices.',
                    'Shortlisted',
                    'Shortlisted based on Java code evaluation score.'
                ),
                (
                    job_map['Data Analyst Intern (Paid)'],
                    user_map['vikram.aditya@gmail.com'],
                    'sample_resume_vikram.pdf',
                    'Skilled in Python Pandas, SQL, and Power BI dashboards with multiple data visualization projects on GitHub.',
                    'Selected',
                    'Selected for Data & Analytics Trainee program! Offer letter issued.'
                ),
                (
                    job_map['UI/UX Design Intern'],
                    user_map['divya.iyer@gmail.com'],
                    'sample_resume_divya.pdf',
                    'Please find attached my resume and link to Behance portfolio containing responsive interactive Figma prototypes.',
                    'Applied',
                    None
                ),
                (
                    job_map['Cloud Support Associate (AWS & Azure)'],
                    user_map['siddharth.rao@gmail.com'],
                    'sample_resume_rahul.pdf',
                    'Enthusiastic about cloud infrastructure with hands-on Linux and basic AWS certification.',
                    'Under Review',
                    'Resume meets foundational cloud requirements.'
                )
            ]

            insert_app_sql = """
                INSERT INTO applications (
                    job_id, fresher_user_id, resume_path, cover_note,
                    status, recruiter_notes, applied_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """
            cur.executemany(q(insert_app_sql), apps_data)

            # 6. Saved Jobs
            saved_jobs_data = [
                (user_map['rahul.sharma@gmail.com'], job_map['Junior Full Stack Developer (React & Node.js)']),
                (user_map['rahul.sharma@gmail.com'], job_map['Data Analyst Intern (Paid)']),
                (user_map['rahul.sharma@gmail.com'], job_map['Associate Software Engineer (Core Systems)']),
                (user_map['ananya.patel@gmail.com'], job_map['Junior Software Developer (Python & SQL)']),
                (user_map['vikram.aditya@gmail.com'], job_map['Data Science Intern']),
                (user_map['divya.iyer@gmail.com'], job_map['Frontend Developer Intern'])
            ]
            cur.executemany(q("INSERT INTO saved_jobs (fresher_user_id, job_id, created_at) VALUES (%s, %s, NOW())"), saved_jobs_data)

            # 7. Notifications
            notifs_data = [
                (
                    user_map['rahul.sharma@gmail.com'],
                    'Interview Scheduled: Python Developer Intern',
                    'Infosys Technologies has scheduled your Technical Interview for Python Developer Intern on Thursday 11:00 AM.',
                    '/fresher/applications',
                    0
                ),
                (
                    user_map['ananya.patel@gmail.com'],
                    'Application Shortlisted',
                    'Infosys Technologies has shortlisted your application for Java Developer Trainee (Spring Boot).',
                    '/fresher/applications',
                    0
                ),
                (
                    user_map['vikram.aditya@gmail.com'],
                    'Congratulations! Selected',
                    'Tata Consultancy Services has selected you for the Data Analyst Intern role! Review offer details in your tracker.',
                    '/fresher/applications',
                    0
                ),
                (
                    user_map['tcs.careers@tcs.com'],
                    'New Candidate Application',
                    'Rahul Sharma applied for Junior Software Developer (Python & SQL).',
                    '/recruiter/applicants',
                    0
                ),
                (
                    user_map['careers@infosys.com'],
                    'New Candidate Application',
                    'Ananya Patel applied for Java Developer Trainee (Spring Boot).',
                    '/recruiter/applicants',
                    1
                )
            ]
            insert_notif_sql = """
                INSERT INTO notifications (user_id, title, message, link, is_read, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cur.executemany(q(insert_notif_sql), notifs_data)

            # 8. Reports
            cur.execute(q("""INSERT INTO reports (reported_by_user_id, job_id, reason, details, status, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """), (
                user_map['rahul.sharma@gmail.com'],
                job_map['Technical Support Engineer (L1)'],
                'Requires clarification on shift allowance',
                'Candidate reported that recruiter should state working shift hours explicitly in the job description.',
                'pending'
            ))

            # 9. Audit Logs
            cur.execute(q("""INSERT INTO audit_logs (user_id, action, details, created_at)
                VALUES (%s, %s, %s, NOW())
            """), (
                user_map['admin@firststep.com'],
                'System Initialized',
                'Platform seeded with 42 fresher-friendly job listings across 6 categories.'
            ))

            conn.commit()
            print(f"Successfully seeded {len(jobs_data)} jobs across all 6 fresher categories!")

    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        if close_at_end:
            conn.close()

if __name__ == '__main__':
    seed_database()
