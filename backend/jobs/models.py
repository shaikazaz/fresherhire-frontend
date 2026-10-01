import uuid

from django.db import models
from django.utils.text import slugify

# Application statuses that use up one of a job's application slots.
SLOT_STATUSES = [
    "applied", "shortlisted", "interview_scheduled", "interview_completed",
    "feedback_given", "offered", "placed", "rejected",
]


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPES = [("full_time", "Full-time"), ("internship", "Internship"),
                 ("part_time", "Part-time"), ("hiring_drive", "Hiring drive")]
    EXP_LEVELS = [("fresher", "Fresher"), ("junior", "0-2 years"), ("mid", "2-5 years")]
    CAP_MODES = [("first_come", "First come"), ("best_match_window", "Best match window")]
    STATUSES = [("draft", "Draft"), ("pending", "Pending approval"), ("active", "Active"), ("closed", "Closed")]

    company = models.ForeignKey("accounts.Company", on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=120)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default="full_time")
    exp_level = models.CharField(max_length=20, choices=EXP_LEVELS, default="fresher")
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    application_cap = models.PositiveIntegerField(default=50)
    cap_mode = models.CharField(max_length=20, choices=CAP_MODES, default="first_come")
    min_match_score = models.PositiveSmallIntegerField(default=40)
    review_window_ends_at = models.DateTimeField(null=True, blank=True)
    response_sla_days = models.PositiveSmallIntegerField(default=7)
    extended_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUSES, default="active")
    jd_score = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "created_at"])]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify("%s %s" % (self.title, self.location))[:200] or "job"
            self.slug = "%s-%s" % (base, uuid.uuid4().hex[:6])
        super().save(*args, **kwargs)

    def __str__(self):
        return "%s at %s" % (self.title, self.company.name)


class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="job_links")
    is_required = models.BooleanField(default=True)

    class Meta:
        unique_together = ("job", "skill")

    def __str__(self):
        return "%s - %s" % (self.job_id, self.skill.name)
