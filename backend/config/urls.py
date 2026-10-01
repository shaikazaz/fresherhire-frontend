from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication
    path("api/auth/", include("accounts.urls")),

    # Jobs
    path("api/", include("jobs.urls")),

    # Applications
    path("api/", include("applications.urls")),

    # Billing
    path("api/billing/", include("billing.urls")),

    # Resumes
    path("api/", include("resumes.urls")),

    # Notifications
    path("api/", include("notifications.urls")),

    # Career guide
    path("api/career/", include("careers.urls")),


]