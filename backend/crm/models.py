from django.conf import settings
from django.db import models


class CrmSyncLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="crm_logs")
    crm_contact_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default="pending")
    response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
