from django.contrib import admin

from .models import Project, Resume, SeekerSkill


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("original_name", "seeker", "ats_score", "passed", "is_active", "uploaded_at")
    list_filter = ("passed", "is_active")


admin.site.register(SeekerSkill)
admin.site.register(Project)
