from django.urls import path
from .views import JobListCreateView,JobDetailView,MyJobsView,RecruiterDashboardView,SkillListView,ExtendCapView,FinalizeBestMatchWindowView
urlpatterns=[path("jobs/",JobListCreateView.as_view()),path("jobs/mine/",MyJobsView.as_view()),path("jobs/skills/",SkillListView.as_view()),path("jobs/<slug:slug>/",JobDetailView.as_view()),path("recruiter/dashboard/",RecruiterDashboardView.as_view()),path("recruiter/jobs/<int:pk>/extend-cap/",ExtendCapView.as_view()),path("recruiter/jobs/<int:pk>/finalize-window/",FinalizeBestMatchWindowView.as_view())]
