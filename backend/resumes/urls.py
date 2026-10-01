from django.urls import path

from .views import ResumeListCreateView, SeekerProfileView

urlpatterns = [
    path("resumes/", ResumeListCreateView.as_view()),
    path("seeker/profile/", SeekerProfileView.as_view()),
]
