from django.contrib import admin

from .models import Job, JobSkill, Skill


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 1


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "job_type", "exp_level", "status", "application_cap", "created_at")
    list_filter = ("status", "job_type", "exp_level")
    search_fields = ("title", "company__name", "location")
    inlines = [JobSkillInline]
    actions = ["approve_jobs", "close_jobs"]

    @admin.action(description="Approve selected jobs (set active)")
    def approve_jobs(self, request, queryset):
        queryset.update(status="active")

    @admin.action(description="Close selected jobs")
    def close_jobs(self, request, queryset):
        queryset.update(status="closed")
