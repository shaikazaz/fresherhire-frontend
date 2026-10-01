from django.urls import path

from .views import (
    ApplicationListCreateView,
    SeekerDashboardView,
    RecruiterApplicantsView,
    ApplicationDecisionView,
    RecruiterFeedbackView,
    InterviewScheduleView,
    InterviewDoneView,
    InterviewConfirmView,
    CandidateSearchView,
    CreateContactUnlockOrderView,
    VerifyContactUnlockPaymentView,
)


urlpatterns = [

    # Seeker
    path(
        "applications/",
        ApplicationListCreateView.as_view(),
        name="applications",
    ),

    path(
        "seeker/dashboard/",
        SeekerDashboardView.as_view(),
        name="seeker-dashboard",
    ),

    # Recruiter
    path(
        "recruiter/applicants/",
        RecruiterApplicantsView.as_view(),
        name="recruiter-applicants",
    ),

    path(
        "applications/<int:pk>/decision/",
        ApplicationDecisionView.as_view(),
        name="application-decision",
    ),

    path(
        "applications/<int:pk>/feedback/",
        RecruiterFeedbackView.as_view(),
        name="application-feedback",
    ),

    path(
        "applications/<int:pk>/interview/",
        InterviewScheduleView.as_view(),
        name="interview-schedule",
    ),

    path(
        "interviews/<int:pk>/done/",
        InterviewDoneView.as_view(),
        name="interview-done",
    ),

    # Seeker confirms interview
    path(
        "interviews/<int:pk>/confirm/",
        InterviewConfirmView.as_view(),
        name="interview-confirm",
    ),

    # Recruiter candidate search
    path(
        "recruiter/candidates/search/",
        CandidateSearchView.as_view(),
        name="candidate-search",
    ),

    # Contact unlock payment
    path(
        "applications/<int:pk>/unlock/create-order/",
        CreateContactUnlockOrderView.as_view(),
        name="contact-unlock-create-order",
    ),

    path(
        "applications/<int:pk>/unlock/verify/",
        VerifyContactUnlockPaymentView.as_view(),
        name="contact-unlock-verify",
    ),
]