from django.contrib import admin

from .models import CrmSyncLog


@admin.register(CrmSyncLog)
class CrmSyncLogAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "crm_contact_id", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email", "crm_contact_id", "response")
    ordering = ("-created_at",)
