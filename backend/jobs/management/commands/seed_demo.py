"""Load demo data: skills, plans, campus, users, companies, 32 jobs and learning resources.

    python manage.py seed_demo
Safe to run more than once.
"""
import random
from datetime import timedelta
from urllib.parse import quote_plus

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Campus, Company, SeekerProfile, User
from billing.models import Plan
from careers.models import SkillResource
from jobs.models import Job, Skill
from jobs.services import set_job_skills

SKILLS = [
    "Python", "Django", "Flask", "JavaScript", "TypeScript", "React", "Node.js", "Express", "HTML", "CSS",
    "Bootstrap", "Tailwind CSS", "SQL", "MySQL", "PostgreSQL", "MongoDB", "Git", "Docker", "AWS", "Linux",
    "REST API", "Java", "Spring Boot", "C++", "Data Structures", "Machine Learning", "Pandas", "NumPy",
    "Scikit-learn", "Excel", "Power BI", "Tableau", "Figma", "Selenium", "Manual Testing", "Communication",
    "Agile", "Kotlin", "Android", "Flutter", "PHP", "Laravel", "Cyber Security", "Networking", "Data Analysis",
]

COMPANIES = [
    ("TechNova Solutions", "IT Services", "recruiter@demo.com"),
    ("Pixel Labs", "Product Startup", "pixel@demo.com"),
    ("DataBridge Analytics", "Analytics", "databridge@demo.com"),
]

# title, skills, exp_level, job_type, location, salary_min, salary_max, cap, min_match
JOBS = [
    ("Python Developer", ["Python", "Django", "SQL", "Git", "REST API"], "fresher", "full_time", "Hyderabad", 300000, 500000, 50, 40),
    ("Junior Django Developer", ["Python", "Django", "MySQL", "REST API"], "fresher", "full_time", "Hyderabad", 320000, 480000, 30, 40),
    ("Frontend Developer (React)", ["JavaScript", "React", "HTML", "CSS", "Git"], "fresher", "full_time", "Bengaluru", 350000, 600000, 40, 40),
    ("React Intern", ["JavaScript", "React", "HTML", "CSS"], "fresher", "internship", "Remote", 120000, 240000, 25, 30),
    ("Full Stack Developer", ["JavaScript", "React", "Node.js", "MongoDB", "REST API"], "junior", "full_time", "Pune", 400000, 700000, 40, 45),
    ("Node.js Backend Developer", ["Node.js", "Express", "MongoDB", "REST API", "Git"], "junior", "full_time", "Chennai", 380000, 650000, 35, 45),
    ("Data Analyst", ["SQL", "Excel", "Power BI", "Data Analysis", "Python"], "fresher", "full_time", "Hyderabad", 300000, 480000, 60, 40),
    ("Business Intelligence Intern", ["SQL", "Tableau", "Excel", "Data Analysis"], "fresher", "internship", "Hyderabad", 100000, 200000, 20, 30),
    ("Machine Learning Engineer", ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn"], "junior", "full_time", "Bengaluru", 500000, 900000, 30, 50),
    ("Data Science Intern", ["Python", "Pandas", "NumPy", "Machine Learning"], "fresher", "internship", "Remote", 150000, 300000, 30, 30),
    ("Java Developer", ["Java", "Spring Boot", "SQL", "REST API", "Git"], "fresher", "full_time", "Hyderabad", 350000, 550000, 50, 40),
    ("Associate Software Engineer", ["Java", "Data Structures", "SQL", "Git"], "fresher", "hiring_drive", "Hyderabad", 300000, 400000, 100, 35),
    ("C++ Developer", ["C++", "Data Structures", "Linux", "Git"], "fresher", "full_time", "Pune", 350000, 600000, 30, 40),
    ("DevOps Engineer", ["Linux", "Docker", "AWS", "Git", "Networking"], "junior", "full_time", "Bengaluru", 500000, 850000, 25, 50),
    ("Cloud Support Associate", ["AWS", "Linux", "Networking", "Communication"], "fresher", "full_time", "Chennai", 300000, 450000, 40, 35),
    ("QA Engineer", ["Manual Testing", "Selenium", "SQL", "Agile"], "fresher", "full_time", "Hyderabad", 280000, 420000, 40, 35),
    ("Automation Test Intern", ["Selenium", "Python", "Manual Testing"], "fresher", "internship", "Hyderabad", 100000, 180000, 20, 30),
    ("UI/UX Designer", ["Figma", "HTML", "CSS", "Communication"], "fresher", "full_time", "Bengaluru", 300000, 500000, 30, 35),
    ("Android Developer", ["Kotlin", "Android", "Git", "REST API"], "junior", "full_time", "Pune", 400000, 700000, 30, 45),
    ("Flutter Developer Intern", ["Flutter", "Git", "REST API"], "fresher", "internship", "Remote", 120000, 240000, 20, 30),
    ("PHP Laravel Developer", ["PHP", "Laravel", "MySQL", "HTML", "CSS"], "fresher", "full_time", "Hyderabad", 280000, 450000, 40, 40),
    ("Cyber Security Analyst", ["Cyber Security", "Networking", "Linux", "Python"], "fresher", "full_time", "Hyderabad", 350000, 600000, 25, 40),
    ("Web Developer Trainee", ["HTML", "CSS", "JavaScript", "Bootstrap"], "fresher", "hiring_drive", "Hyderabad", 220000, 320000, 80, 30),
    ("Backend Engineer (Python)", ["Python", "Flask", "PostgreSQL", "Docker", "AWS"], "mid", "full_time", "Bengaluru", 700000, 1200000, 20, 55),
    ("Python FastAPI Developer", ["Python", "REST API", "PostgreSQL", "Docker", "Git"], "junior", "full_time", "Hyderabad", 400000, 700000, 30, 45),
    ("SQL Developer", ["SQL", "MySQL", "PostgreSQL", "Python", "Git"], "fresher", "full_time", "Chennai", 300000, 500000, 40, 35),
    ("React Frontend Intern", ["React", "JavaScript", "HTML", "CSS", "Git"], "fresher", "internship", "Pune", 120000, 220000, 25, 30),
    ("Cloud Engineer Trainee", ["AWS", "Linux", "Docker", "Networking", "Git"], "fresher", "hiring_drive", "Hyderabad", 300000, 500000, 60, 40),
    ("Python Automation Tester", ["Python", "Selenium", "SQL", "Git", "Manual Testing"], "fresher", "full_time", "Bengaluru", 300000, 520000, 35, 40),
    ("Junior Data Engineer", ["Python", "SQL", "Pandas", "AWS", "Docker"], "junior", "full_time", "Pune", 450000, 750000, 25, 45),
    ("Java Backend Intern", ["Java", "Spring Boot", "SQL", "REST API", "Git"], "fresher", "internship", "Chennai", 120000, 240000, 25, 30),
    ("Technical Support Engineer", ["Linux", "Networking", "SQL", "Communication", "AWS"], "fresher", "full_time", "Hyderabad", 280000, 450000, 50, 35),
]

COURSES = {
    "Python": ("Python for Everybody", "Build a small automation script or CLI tool"),
    "Django": ("Django tutorial for beginners", "Build a blog with login, posts and comments"),
    "React": ("React full course", "Build a job search UI with filters"),
    "JavaScript": ("JavaScript fundamentals", "Build a to-do app with local filtering"),
    "SQL": ("SQL for beginners", "Design a library database and write 15 queries"),
    "MySQL": ("MySQL tutorial", "Create a schema with joins for an online store"),
    "Git": ("Git and GitHub crash course", "Publish 3 projects on GitHub with good READMEs"),
    "Docker": ("Docker for beginners", "Containerize a Django or Node app"),
    "AWS": ("AWS cloud practitioner basics", "Host a static site on S3"),
    "Node.js": ("Node.js crash course", "Build a REST API for notes"),
    "REST API": ("REST API design basics", "Build and document a CRUD API"),
    "Machine Learning": ("Machine learning basics", "Predict house prices with scikit-learn"),
    "Power BI": ("Power BI for beginners", "Build a sales dashboard from a public dataset"),
    "Excel": ("Excel for data analysis", "Analyze a sales sheet with pivot tables"),
    "Java": ("Java programming for beginners", "Build a console banking app"),
    "Selenium": ("Selenium automation testing", "Automate login tests for a demo site"),
    "Linux": ("Linux command line basics", "Write shell scripts to automate backups"),
    "Figma": ("Figma UI design basics", "Design a 5-screen mobile app prototype"),
    "MongoDB": ("MongoDB crash course", "Add a MongoDB database to a Node API"),
    "HTML": ("HTML and CSS full course", "Recreate a landing page from a screenshot"),
}

PLANS = [
    ("Free", 0, 1, 20, {"candidate_search": False}),
    ("Starter", 1999, 5, 100, {"candidate_search": True}),
    ("Growth", 4999, 20, 500, {"candidate_search": True, "priority_listing": True, "contact_unlock": True}),
    ("Enterprise", 0, 1000, 100000, {"campus_hiring": True, "custom_pricing": True}),
]


def search_url(kind, query):
    if kind == "course":
        return "https://www.youtube.com/results?search_query=" + quote_plus(query)
    return "https://github.com/search?q=" + quote_plus(query) + "&type=repositories"


class Command(BaseCommand):
    help = "Load demo data (safe to run repeatedly)."

    def handle(self, *args, **options):
        random.seed(7)
        for name in SKILLS:
            Skill.objects.get_or_create(name=name)

        for name, price, limit, views, features in PLANS:
            Plan.objects.update_or_create(name=name, defaults={
                "price": price, "job_limit": limit, "candidate_views": views, "features_json": features})

        Campus.objects.get_or_create(invite_code="jntu-hyd", defaults={"name": "JNTU Hyderabad", "city": "Hyderabad"})
        Campus.objects.get_or_create(invite_code="osmania", defaults={"name": "Osmania University", "city": "Hyderabad"})

        if not User.objects.filter(email="admin@demo.com").exists():
            User.objects.create_superuser("admin@demo.com", "Admin@12345", full_name="Platform Admin", is_verified=True)

        companies = []
        for name, industry, email in COMPANIES:
            user = User.objects.filter(email=email).first()
            if user is None:
                user = User.objects.create_user(email, "Recruiter@123", full_name=name + " HR",
                                                role="recruiter", is_verified=True)
            company, _ = Company.objects.get_or_create(
                recruiter_user=user, defaults={"name": name, "industry": industry, "is_verified": True,
                                               "website": "https://example.com"})
            companies.append(company)

        seeker = User.objects.filter(email="seeker@demo.com").first()
        if seeker is None:
            seeker = User.objects.create_user("seeker@demo.com", "Seeker@123", full_name="Ananya Reddy", role="seeker")
        SeekerProfile.objects.get_or_create(user=seeker, defaults={
            "full_name": "Ananya Reddy", "location": "Hyderabad",
            "campus": Campus.objects.get(invite_code="jntu-hyd")})

        created = 0
        now = timezone.now()
        for i, (title, skills, exp, jtype, loc, smin, smax, cap, minm) in enumerate(JOBS):
            company = companies[i % len(companies)]
            if Job.objects.filter(company=company, title=title).exists():
                continue
            job = Job.objects.create(
                company=company, title=title, location=loc, job_type=jtype, exp_level=exp,
                salary_min=smin, salary_max=smax, application_cap=cap, min_match_score=minm,
                description=("We are hiring a %s. You will work with %s to build and improve real products, "
                             "learn from senior engineers and take ownership of small features. Freshers with "
                             "strong projects are welcome." % (title, ", ".join(skills))))
            set_job_skills(job, skills)
            Job.objects.filter(pk=job.pk).update(created_at=now - timedelta(hours=random.randint(1, 240)))
            created += 1

        for skill_name, (course, project) in COURSES.items():
            skill = Skill.objects.filter(name=skill_name).first()
            if skill is None:
                continue
            SkillResource.objects.get_or_create(skill=skill, kind="course", title=course, defaults={
                "provider": "YouTube search", "url": search_url("course", course)})
            SkillResource.objects.get_or_create(skill=skill, kind="project", title=project, defaults={
                "provider": "GitHub examples", "url": search_url("project", skill_name + " project")})

        self.stdout.write(self.style.SUCCESS("Seed complete: %d new jobs." % created))
        self.stdout.write("Admin     admin@demo.com      / Admin@12345")
        self.stdout.write("Recruiter recruiter@demo.com  / Recruiter@123")
        self.stdout.write("Seeker    seeker@demo.com     / Seeker@123")
