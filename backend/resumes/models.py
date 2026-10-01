from django.db import models


class Resume(models.Model):
    seeker = models.ForeignKey("accounts.SeekerProfile", on_delete=models.CASCADE, related_name="resumes")
    file = models.FileField(upload_to="resumes/%Y/%m/")
    original_name = models.CharField(max_length=255, blank=True)
    parsed_text = models.TextField(blank=True)
    projects_text = models.TextField(blank=True)
    ats_score = models.PositiveSmallIntegerField(default=0)
    ats_report = models.JSONField(default=dict, blank=True)
    passed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return "%s (%s)" % (self.original_name or self.file.name, self.ats_score)


class SeekerSkill(models.Model):
    SOURCES = [("resume", "From resume"), ("manual", "Added manually")]

    seeker = models.ForeignKey("accounts.SeekerProfile", on_delete=models.CASCADE, related_name="seeker_skills")
    skill = models.ForeignKey("jobs.Skill", on_delete=models.CASCADE, related_name="seeker_links")
    source = models.CharField(max_length=10, choices=SOURCES, default="resume")

    class Meta:
        unique_together = ("seeker", "skill")

    def __str__(self):
        return "%s - %s" % (self.seeker_id, self.skill.name)


class Project(models.Model):
    seeker = models.ForeignKey("accounts.SeekerProfile", on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tech_stack = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.title
