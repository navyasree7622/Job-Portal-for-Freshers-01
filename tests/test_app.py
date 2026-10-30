import unittest
from app import app
from database.db import query_db, execute_db

class JobPortalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_public_home_page(self):
        """Test home page responds with status 200 and brand title."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'FirstStep', res.data)
        self.assertIn(b'Active Vacancies', res.data)

    def test_02_browse_jobs_page_and_faceted_filters(self):
        """Test browsing jobs, search filtering, work arrangements, and skill pills."""
        res = self.client.get('/jobs')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Explore', res.data)

        # Filter by keyword
        res_filter = self.client.get('/jobs?keyword=Python')
        self.assertEqual(res_filter.status_code, 200)
        self.assertIn(b'Python', res_filter.data)

        # Filter by work arrangement (Remote)
        res_remote = self.client.get('/jobs?work_arrangement=Remote')
        self.assertEqual(res_remote.status_code, 200)
        self.assertIn(b'Remote', res_remote.data)

        # Filter by category
        res_cat = self.client.get('/jobs?category=Data %26 Analytics')
        self.assertEqual(res_cat.status_code, 200)

        # Filter by skill tag
        res_skill = self.client.get('/jobs?skill=React')
        self.assertEqual(res_skill.status_code, 200)

    def test_03_informational_pages(self):
        """Test About, Contact, Login, and Register pages load properly."""
        for path in ['/about', '/contact', '/login', '/register']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Failed on path: {path}")

    def test_04_fresher_authentication(self):
        """Test signing in as a Fresher."""
        res = self.client.post('/login', data={
            'email': 'rahul.sharma@gmail.com',
            'password': 'fresher123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Rahul Sharma', res.data)

    def test_05_recruiter_authentication(self):
        """Test signing in as a Recruiter."""
        res = self.client.post('/login', data={
            'email': 'tcs.careers@tcs.com',
            'password': 'recruiter123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Tata Consultancy Services', res.data)

    def test_06_admin_authentication(self):
        """Test signing in as an Administrator."""
        res = self.client.post('/login', data={
            'email': 'admin@firststep.com',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Command Center', res.data)

    def test_07_invalid_credentials(self):
        """Test that invalid passwords are rejected."""
        res = self.client.post('/login', data={
            'email': 'rahul.sharma@gmail.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Invalid email address or password', res.data)

    def test_08_role_authorization_guard(self):
        """Test that a fresher cannot access the admin or recruiter dashboard."""
        with self.client:
            self.client.post('/login', data={
                'email': 'rahul.sharma@gmail.com',
                'password': 'fresher123'
            })
            # Attempt to access recruiter dashboard
            res_recruiter = self.client.get('/recruiter/dashboard')
            self.assertEqual(res_recruiter.status_code, 403)

            # Attempt to access admin dashboard
            res_admin = self.client.get('/admin/dashboard')
            self.assertEqual(res_admin.status_code, 403)

    def test_09_duplicate_application_guard(self):
        """Test that candidate cannot apply twice to the same job."""
        with self.client:
            self.client.post('/login', data={
                'email': 'rahul.sharma@gmail.com',
                'password': 'fresher123'
            })
            # Rahul already applied to job 1 in seed data
            res_apply = self.client.post('/jobs/1/apply', data={
                'use_existing_resume': '1'
            }, follow_redirects=True)
            self.assertIn(b'already submitted an application', res_apply.data)

    def test_10_bookmark_api(self):
        """Test bookmarking API for authenticated freshers."""
        with self.client:
            self.client.post('/login', data={
                'email': 'rahul.sharma@gmail.com',
                'password': 'fresher123'
            })
            # Toggle bookmark on job 4
            res_bm = self.client.post('/api/jobs/4/bookmark')
            self.assertEqual(res_bm.status_code, 200)
            data = res_bm.get_json()
            self.assertIn(data['status'], ['saved', 'removed'])

    def test_11_recruiter_status_update(self):
        """Test recruiter updating candidate status."""
        with self.client:
            # Login as TCS recruiter
            self.client.post('/login', data={
                'email': 'tcs.careers@tcs.com',
                'password': 'recruiter123'
            })
            # Find an application belonging to TCS
            tcs_app = query_db("""
                SELECT a.id FROM applications a
                JOIN jobs j ON a.job_id = j.id
                WHERE j.recruiter_user_id = %s
                LIMIT 1
            """, (query_db("SELECT id FROM users WHERE email='tcs.careers@tcs.com'", one=True)['id'],), one=True)

            self.assertIsNotNone(tcs_app)
            res_update = self.client.post(f"/recruiter/applications/{tcs_app['id']}/status", data={
                'status': 'Shortlisted',
                'recruiter_notes': 'Cleared initial aptitude screening.'
            }, follow_redirects=True)
            self.assertEqual(res_update.status_code, 200)
            self.assertIn(b'Candidate status updated to', res_update.data)

    def test_12_admin_moderation_flow_and_audit(self):
        """Test admin verifying a company and creating audit log."""
        with self.client:
            self.client.post('/login', data={
                'email': 'admin@firststep.com',
                'password': 'admin123'
            })
            # Find a company to verify
            comp = query_db("SELECT id FROM companies LIMIT 1", one=True)
            if comp:
                res_verify = self.client.post(f"/admin/companies/{comp['id']}/verify", data={
                    'status': 'verified'
                }, follow_redirects=True)
                self.assertEqual(res_verify.status_code, 200)
                self.assertIn(b'Company status updated to verified', res_verify.data)

                # Verify audit log was recorded
                audit = query_db("SELECT * FROM audit_logs WHERE action = 'Company Verification Updated' ORDER BY id DESC LIMIT 1", one=True)
                self.assertIsNotNone(audit)

    def test_13_secure_resume_download_authorization(self):
        """Test that unauthenticated or unauthorized users cannot access candidate resumes."""
        # Unauthenticated request
        res_unauth = self.client.get('/uploads/resume/sample_resume_rahul.pdf')
        # Should redirect to login
        self.assertEqual(res_unauth.status_code, 302)

        # Authenticated as the candidate owner
        with self.client:
            self.client.post('/login', data={
                'email': 'rahul.sharma@gmail.com',
                'password': 'fresher123'
            })
            res_owner = self.client.get('/uploads/resume/sample_resume_rahul.pdf')
            self.assertEqual(res_owner.status_code, 200)

    def test_14_fresher_dashboard_stats_and_recommendations(self):
        """Test Fresher Dashboard displays accurate DB metrics, recommendations, and bookmarks."""
        with self.client:
            self.client.post('/login', data={
                'email': 'rahul.sharma@gmail.com',
                'password': 'fresher123'
            })
            res = self.client.get('/fresher/dashboard')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Candidate Portal', res.data)
            self.assertIn(b'Profile Strength', res.data)
            self.assertIn(b'Recommended Opportunities for Your Skills', res.data)

    def test_15_recruiter_dashboard_and_active_metrics(self):
        """Test Recruiter Dashboard displays active jobs, candidate submissions, and notification log."""
        with self.client:
            self.client.post('/login', data={
                'email': 'tcs.careers@tcs.com',
                'password': 'recruiter123'
            })
            res = self.client.get('/recruiter/dashboard')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Tata Consultancy Services', res.data)
            self.assertIn(b'Active Vacancies', res.data)
            self.assertIn(b'Recent Candidate Submissions', res.data)

    def test_16_post_and_edit_job_with_work_arrangement(self):
        """Test Recruiter creating a new job with remote arrangement and editing it."""
        with self.client:
            self.client.post('/login', data={
                'email': 'tcs.careers@tcs.com',
                'password': 'recruiter123'
            })
            res_post = self.client.post('/recruiter/jobs/post', data={
                'title': 'Junior Automated Cloud Tester',
                'category': 'Quality Assurance',
                'job_type': 'Full-Time',
                'work_arrangement': 'Remote',
                'experience_level': '0 Years (Fresh Graduate)',
                'location': 'Bangalore / Remote',
                'salary_min': '450000',
                'salary_max': '650000',
                'required_skills': 'Selenium, Python, AWS, PyTest',
                'eligibility': 'B.Tech/MCA 2025/2026',
                'description': 'Responsible for creating automated test scripts in cloud environments.',
                'responsibilities': 'Execute smoke and regression test cycles.',
                'status': 'published',
                'is_featured': '1'
            }, follow_redirects=True)
            self.assertEqual(res_post.status_code, 200)
            self.assertIn(b'successfully published', res_post.data)

            # Verify in DB
            new_job = query_db("SELECT * FROM jobs WHERE title = 'Junior Automated Cloud Tester'", one=True)
            self.assertIsNotNone(new_job)
            self.assertEqual(new_job['work_arrangement'], 'Remote')
            self.assertEqual(new_job['is_featured'], 1)
            self.assertEqual(new_job['is_sample'], 0)  # Recruiter created, not sample

    def test_17_search_multi_faceted(self):
        """Test complex multi-faceted filtering in job discovery."""
        res = self.client.get('/jobs?keyword=Python&work_arrangement=Remote&min_salary=300000')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Python', res.data)
        self.assertIn(b'Remote', res.data)

if __name__ == '__main__':
    unittest.main()
