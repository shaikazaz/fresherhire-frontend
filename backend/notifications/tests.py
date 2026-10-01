from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from accounts.models import SeekerProfile,Company
from jobs.models import Job,Skill,JobSkill
from notifications.models import Notification
from notifications.services import notify_matching_seekers

class NotificationTests(TestCase):
    def test_matching_job_creates_notification_and_email(self):
        U=get_user_model(); seeker=U.objects.create_user(email="s@test.com",password="Pass12345",full_name="Seeker",role="seeker")
        SeekerProfile.objects.create(user=seeker,full_name="Seeker",experience_level="fresher",education="BTech",location="Hyderabad")
        recruiter=U.objects.create_user(email="r@test.com",password="Pass12345",full_name="Recruiter",role="recruiter")
        company=Company.objects.create(recruiter_user=recruiter,name="Test Co")
        skill=Skill.objects.create(name="Python")
        job=Job.objects.create(company=company,title="Python Fresher",location="Hyderabad",description="Python developer",status="active",min_match_score=0)
        JobSkill.objects.create(job=job,skill=skill)
        result=notify_matching_seekers(job)
        self.assertEqual(result["notifications"],1)
        self.assertEqual(Notification.objects.count(),1)
