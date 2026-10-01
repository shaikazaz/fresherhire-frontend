"""API tests. Run with: python manage.py test"""
import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from docx import Document
from rest_framework.test import APITestCase

from accounts.models import Company, User
from jobs.models import Job, Skill
from jobs.services import set_job_skills

RESUME_LINES = [
    ("Asha Rao", None),
    ("Hyderabad | asha.rao@example.com | +91 98765 12345", None),
    ("linkedin.com/in/asharao | github.com/asharao", None),
    ("Education", "H"),
    ("B.Tech in Computer Science, JNTU Hyderabad, 2021 - 2025", None),
    ("Skills", "H"),
    ("Python, Django, SQL, MySQL, Git, HTML, CSS, JavaScript, REST API, Docker", None),
    ("Projects", "H"),
    ("Built a job portal with Django and MySQL used by 50 students and improved search speed by 30%.", None),
    ("Developed a Python resume scanner that analyzed 200+ resumes and automated keyword checks.", None),
    ("Designed a REST API and deployed it with Docker; reduced manual work by 40%.", None),
    ("Internships", "H"),
    ("Python Intern, TechNova, Jun 2024 - Aug 2024", None),
    ("Implemented reports with SQL and collaborated with 4 engineers to test and deploy features.", None),
]


def resume_file():
    doc = Document()
    for text, kind in RESUME_LINES:
        doc.add_heading(text, level=2) if kind == "H" else doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return SimpleUploadedFile("resume.docx", buf.getvalue(),
                              content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


class PortalFlowTests(APITestCase):
    def setUp(self):
        for name in ["Python", "Django", "SQL", "MySQL", "Git", "HTML", "CSS", "JavaScript", "REST API", "Docker"]:
            Skill.objects.create(name=name)
        recruiter = User.objects.create_user("hr@x.com", "Recruiter@123", full_name="HR", role="recruiter")
        self.company = Company.objects.create(recruiter_user=recruiter, name="TestCo", is_verified=True)
        self.job = Job.objects.create(company=self.company, title="Python Developer", location="Hyderabad",
                                      description="Build Django APIs with MySQL", application_cap=1,
                                      min_match_score=30)
        set_job_skills(self.job, ["Python", "Django", "SQL"])

    def register_seeker(self):
        res = self.client.post("/api/auth/register/", {
            "email": "asha@x.com", "password": "Seeker@123", "full_name": "Asha Rao", "role": "seeker"}, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + res.json()["access"])

    def test_register_login_roles_and_me(self):
        self.register_seeker()
        self.client.credentials()
        res = self.client.post("/api/auth/login/", {"email": "asha@x.com", "password": "Seeker@123"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["user"]["role"], "seeker")
        dup = self.client.post("/api/auth/register/", {
            "email": "ASHA@x.com", "password": "Seeker@123", "full_name": "A", "role": "seeker"}, format="json")
        self.assertEqual(dup.status_code, 400)

    def test_public_job_list_and_filters(self):
        res = self.client.get("/api/jobs/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["count"], 1)
        self.assertEqual(self.client.get("/api/jobs/?location=Pune").json()["count"], 0)
        self.assertEqual(self.client.get("/api/jobs/?skills=python").json()["count"], 1)
        self.assertEqual(self.client.get("/api/jobs/?job_type=internship").json()["count"], 0)
        self.assertEqual(self.client.get("/api/jobs/" + self.job.slug + "/").status_code, 200)

    def test_apply_requires_resume_then_waitlist(self):
        self.register_seeker()
        blocked = self.client.post("/api/applications/", {"job_id": self.job.id}, format="json")
        self.assertEqual(blocked.status_code, 400)

        with override_settings(ATS_PASS_SCORE=60):
            up = self.client.post("/api/resumes/", {"file": resume_file()}, format="multipart")
        self.assertEqual(up.status_code, 201, up.content)
        self.assertTrue(up.json()["passed"], up.json()["report"]["fixes"])

        jobs = self.client.get("/api/jobs/").json()
        self.assertTrue(jobs["has_resume"])
        self.assertIsNotNone(jobs["results"][0]["match_score"])

        ok = self.client.post("/api/applications/", {"job_id": self.job.id}, format="json")
        self.assertEqual(ok.status_code, 201, ok.content)
        self.assertEqual(ok.json()["application"]["status"], "applied")
        again = self.client.post("/api/applications/", {"job_id": self.job.id}, format="json")
        self.assertEqual(again.status_code, 400)

        dash = self.client.get("/api/seeker/dashboard/").json()
        self.assertEqual(dash["counters"]["applied"], 1)
        self.assertEqual(self.client.get("/api/career/guide/").status_code, 200)

    def test_role_permissions(self):
        self.register_seeker()
        self.assertEqual(self.client.get("/api/jobs/mine/").status_code, 403)
        post = self.client.post("/api/jobs/", {"title": "x"}, format="json")
        self.assertEqual(post.status_code, 403)

    def test_recruiter_can_post_job(self):
        login = self.client.post("/api/auth/login/", {"email": "hr@x.com", "password": "Recruiter@123"}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.json()["access"])
        res = self.client.post("/api/jobs/", {
            "title": "React Intern", "description": "Build UI", "location": "Remote", "job_type": "internship",
            "exp_level": "fresher", "application_cap": 10, "min_match_score": 30, "skills": ["React", "HTML"]},
            format="json")
        self.assertEqual(res.status_code, 201, res.content)
        self.assertTrue(res.json()["slug"].startswith("react-intern"))
        self.assertEqual(len(self.client.get("/api/jobs/mine/").json()), 2)
