from django.contrib import admin

from .models import Application, Feedback, Interview


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "seeker", "match_score", "status", "applied_at")
    list_filter = ("status",)


admin.site.register(Interview)
admin.site.register(Feedback)
