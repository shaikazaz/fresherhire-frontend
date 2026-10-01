from django.db import models


class SkillResource(models.Model):
    KINDS = [("course", "Course"), ("project", "Project idea")]

    skill = models.ForeignKey("jobs.Skill", on_delete=models.CASCADE, related_name="resources")
    kind = models.CharField(max_length=10, choices=KINDS, default="course")
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)
    provider = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return "%s: %s" % (self.skill.name, self.title)
