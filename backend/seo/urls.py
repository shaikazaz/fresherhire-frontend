from django.urls import path
from .views import JobSeoDetailView, JobSeoListView
urlpatterns=[path("jobs/",JobSeoListView.as_view(),name="seo-job-list"),path("jobs/<slug:slug>/",JobSeoDetailView.as_view(),name="seo-job-detail")]
