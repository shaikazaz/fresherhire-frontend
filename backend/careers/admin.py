from django.contrib import admin

from .models import SkillResource


@admin.register(SkillResource)
class SkillResourceAdmin(admin.ModelAdmin):
    list_display = ("skill", "kind", "title", "provider")
    list_filter = ("kind",)
