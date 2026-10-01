from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework.exceptions import (
    NotFound,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Campus
from accounts.permissions import (
    IsRecruiter,
    IsSeeker,
)

from jobs.models import (
    SLOT_STATUSES,
    Job,
)

from jobs.serializers import JobSerializer

from jobs.services import (
    base_queryset,
    slots_left,
)

from .match import compute_match

from .models import (
    Application,
    ContactUnlock,
    Interview,
    Feedback,
)

from .services import (
    job_to_dict,
    seeker_context,
)


def application_payload(
    app,
    contact=False,
):
    feedback = getattr(
        app,
        "feedback",
        None,
    )

    seeker = app.seeker

    data = {
        "id": app.id,
        "status": app.status,
        "match_score": app.match_score,
        "applied_at": app.applied_at,

        "job": {
            "slug": app.job.slug,
            "title": app.job.title,
            "company": app.job.company.name,
            "location": app.job.location,
            "job_type": app.job.job_type,
        },

        "feedback": (
            {
                "reason_code": feedback.reason_code,
                "comments": feedback.comments,
                "is_system_generated": (
                    feedback.is_system_generated
                ),
                "missing_skills": (
                    feedback.missing_skills_json
                ),
            }
            if feedback
            else None
        ),

        "response_due_at": app.response_due_at,

        "responded_at": app.responded_at,

        "sla_status": (
            "responded"
            if app.responded_at
            else (
                "overdue"
                if (
                    app.response_due_at
                    and app.response_due_at < timezone.now()
                )
                else "within_sla"
            )
        ),

        "interview": (
            {
                "id": app.interview.id,
                "scheduled_at": app.interview.scheduled_at,
                "mode": app.interview.mode,
                "recruiter_marked_done": (
                    app.interview.recruiter_marked_done
                ),
                "seeker_confirmed": (
                    app.interview.seeker_confirmed
                ),
            }
            if hasattr(app, "interview")
            else None
        ),

        "contact_unlocked": bool(contact),
    }

    if contact:
        data["candidate"] = {
            "id": seeker.id,

            "name": (
                seeker.full_name
                or seeker.user.full_name
            ),

            "email": seeker.user.email,

            "phone": seeker.phone,

            "location": seeker.location,

            "education": seeker.education,

            "grad_year": seeker.grad_year,

            "experience_level": (
                seeker.experience_level
            ),

            "campus": (
                seeker.campus.name
                if seeker.campus
                else None
            ),
        }

    return data


class ApplicationListCreateView(APIView):
    permission_classes = [
        IsSeeker
    ]

    def get(self, request):
        applications = (
            request.user
            .seeker_profile
            .applications
            .select_related(
                "job__company",
                "feedback",
                "interview",
            )
            .order_by("-applied_at")
        )

        return Response(
            [
                application_payload(
                    application
                )
                for application in applications
            ]
        )

    def post(self, request):
        profile = (
            request.user.seeker_profile
        )

        job_id = request.data.get(
            "job_id"
        )

        try:
            job = (
                Job.objects
                .select_related("company")
                .prefetch_related(
                    "job_skills__skill"
                )
                .get(
                    pk=int(job_id),
                    status="active",
                )
            )

        except (
            TypeError,
            ValueError,
            Job.DoesNotExist,
        ):
            raise NotFound(
                "This job is not available."
            )

        context = seeker_context(
            request.user
        )

        if context is None:
            raise ValidationError(
                {
                    "detail": (
                        "Upload a resume that "
                        "passes the ATS scan "
                        "before applying."
                    )
                }
            )

        already_applied = (
            Application.objects.filter(
                job=job,
                seeker=profile,
            ).exists()
        )

        if already_applied:
            raise ValidationError(
                {
                    "detail": (
                        "You have already "
                        "applied to this job."
                    )
                }
            )

        match = compute_match(
            context,
            job_to_dict(job),
        )

        if (
            match["score"]
            < job.min_match_score
        ):
            return Response(
                {
                    "detail": (
                        f"Your match score is "
                        f"{match['score']} and "
                        f"this job needs at "
                        f"least "
                        f"{job.min_match_score}."
                    ),
                    "match": match,
                },
                status=400,
            )

        try:
            with transaction.atomic():

                locked_job = (
                    Job.objects
                    .select_for_update()
                    .get(
                        pk=job.pk
                    )
                )

                used = (
                    Application.objects
                    .filter(
                        job=locked_job,
                        status__in=SLOT_STATUSES,
                    )
                    .count()
                )

                if (
                    locked_job.cap_mode
                    == "best_match_window"
                    and locked_job.review_window_ends_at
                    and locked_job.review_window_ends_at
                    > timezone.now()
                ):
                    status = "waitlisted"

                else:
                    status = (
                        "waitlisted"
                        if used
                        >= locked_job.application_cap
                        else "applied"
                    )

                application = (
                    Application.objects.create(
                        job=locked_job,
                        seeker=profile,
                        resume=context["resume"],
                        match_score=match[
                            "score"
                        ],
                        status=status,
                        response_due_at=(
                            timezone.now()
                            + timedelta(
                                days=(
                                    locked_job
                                    .response_sla_days
                                )
                            )
                        ),
                    )
                )

        except IntegrityError:
            raise ValidationError(
                {
                    "detail": (
                        "You have already "
                        "applied to this job."
                    )
                }
            )

        message = (
            "Application submitted."
            if status == "applied"
            else (
                "This job is full, so you "
                "have been added to the "
                "waitlist."
            )
        )

        return Response(
            {
                "detail": message,
                "application": {
                    "id": application.id,
                    "status": application.status,
                    "match_score": (
                        application.match_score
                    ),
                },
            },
            status=201,
        )


class SeekerDashboardView(APIView):
    permission_classes = [
        IsSeeker
    ]

    def get(self, request):
        profile = (
            request.user.seeker_profile
        )

        context = seeker_context(
            request.user
        )

        applied_status = dict(
            profile.applications.values_list(
                "job_id",
                "status",
            )
        )

        eligible = 0
        scored = []

        if context:
            for job in (
                base_queryset()
                .filter(status="active")
            ):
                match = compute_match(
                    context,
                    job_to_dict(job),
                )

                if (
                    match["score"]
                    >= job.min_match_score
                ):
                    eligible += 1

                    if (
                        job.id
                        not in applied_status
                    ):
                        scored.append(
                            (
                                match,
                                job,
                            )
                        )

        scored.sort(
            key=lambda item: (
                slots_left(item[1]) == 0,
                -item[0]["score"],
                -item[1].created_at.timestamp(),
            )
        )

        top = scored[:5]

        top_data = JobSerializer(
            [
                job
                for _, job in top
            ],
            many=True,
            context={
                "matches": {
                    job.id: match
                    for match, job in top
                },
                "applied": applied_status,
            },
        ).data

        applications = (
            profile.applications
            .exclude(status="withdrawn")
        )

        recent = (
            profile.applications
            .select_related(
                "job__company",
                "feedback",
                "interview",
            )
            .order_by("-applied_at")[:5]
        )

        checks = [
            profile.full_name,
            profile.phone,
            profile.location,
            profile.education,
            profile.grad_year,
            profile.seeker_skills.exists(),
            context is not None,
        ]

        completion = round(
            100
            * sum(
                1
                for check in checks
                if check
            )
            / len(checks)
        )

        return Response(
            {
                "counters": {
                    "eligible": eligible,

                    "applied": applications.count(),

                    "placed": applications.filter(
                        status__in=[
                            "offered",
                            "placed",
                        ]
                    ).count(),

                    "waitlisted": applications.filter(
                        status="waitlisted"
                    ).count(),
                },

                "ats_score": profile.ats_score,

                "has_resume": (
                    context is not None
                ),

                "profile_completion": completion,

                "top_matches": top_data,

                "recent_applications": [
                    application_payload(
                        application
                    )
                    for application in recent
                ],
            }
        )


class RecruiterApplicantsView(APIView):
    permission_classes = [
        IsRecruiter
    ]

    def get(self, request):
        queryset = (
            Application.objects
            .filter(
                job__company__recruiter_user=request.user
            )
            .select_related(
                "job",
                "job__company",
                "seeker__user",
                "seeker__campus",
                "feedback",
                "interview",
            )
            .order_by(
                "-match_score",
                "applied_at",
            )
        )

        job_id = request.query_params.get(
            "job_id"
        )

        if job_id:
            queryset = queryset.filter(
                job_id=job_id
            )

        return Response(
            [
                application_payload(
                    application,
                    contact=(
                        hasattr(
                            application,
                            "contact_unlock",
                        )
                        and application.contact_unlock.unlocked
                    ),
                )
                for application in queryset
            ]
        )


ALLOWED_TRANSITIONS = {
    "waitlisted": {
        "applied",
        "withdrawn",
    },

    "applied": {
        "shortlisted",
        "rejected",
        "withdrawn",
    },

    "shortlisted": {
        "interview_scheduled",
        "rejected",
        "withdrawn",
    },

    "interview_scheduled": {
        "interview_completed",
        "withdrawn",
    },

    "interview_completed": {
        "feedback_given",
        "rejected",
    },

    "feedback_given": {
        "offered",
        "rejected",
    },

    "offered": {
        "placed",
        "rejected",
    },

    "placed": set(),

    "rejected": set(),

    "withdrawn": set(),
}


class ApplicationDecisionView(APIView):
    permission_classes = [
        IsRecruiter
    ]

    def patch(self, request, pk):
        application = (
            Application.objects
            .select_related(
                "job__company",
                "seeker",
                "feedback",
                "interview",
            )
            .filter(pk=pk)
            .first()
        )

        if not application:
            raise NotFound(
                "Application not found."
            )

        if (
            application
            .job
            .company
            .recruiter_user_id
            != request.user.id
        ):
            return Response(
                {
                    "detail": "Forbidden"
                },
                status=403,
            )

        new_status = request.data.get(
            "status"
        )

        if new_status not in dict(
            Application.STATUSES
        ):
            raise ValidationError(
                {
                    "status": (
                        "Invalid status."
                    )
                }
            )

        if new_status == application.status:
            raise ValidationError(
                {
                    "status": (
                        "Application is "
                        "already in this status."
                    )
                }
            )

        allowed = ALLOWED_TRANSITIONS.get(
            application.status,
            set(),
        )

        if new_status not in allowed:
            raise ValidationError(
                {
                    "status": (
                        f"Cannot change "
                        f"application from "
                        f"'{application.status}' "
                        f"to "
                        f"'{new_status}'."
                    )
                }
            )

        reason_code = (
            request.data.get(
                "reason_code"
            )
            or ""
        ).strip()

        comments = (
            request.data.get(
                "comments"
            )
            or ""
        ).strip()

        if (
            new_status == "rejected"
            and not reason_code
        ):
            raise ValidationError(
                {
                    "reason_code": (
                        "A rejection reason "
                        "is required."
                    )
                }
            )

        application.status = new_status

        application.responded_at = (
            timezone.now()
        )

        application.save(
            update_fields=[
                "status",
                "responded_at",
            ]
        )

        if new_status == "rejected":
            Feedback.objects.update_or_create(
                application=application,
                defaults={
                    "reason_code": reason_code,
                    "comments": comments,
                    "is_system_generated": False,
                },
            )

        return Response(
            application_payload(
                application,
                contact=(
                    hasattr(
                        application,
                        "contact_unlock",
                    )
                    and application.contact_unlock.unlocked
                ),
            )
        )


class RecruiterFeedbackView(APIView):
    permission_classes = [
        IsRecruiter
    ]

    def post(self, request, pk):
        application = (
            Application.objects
            .select_related(
                "job__company",
                "interview",
            )
            .filter(pk=pk)
            .first()
        )

        if not application:
            raise NotFound(
                "Application not found."
            )

        if (
            application.job.company.recruiter_user_id
            != request.user.id
        ):
            return Response(
                {
                    "detail": "Forbidden"
                },
                status=403,
            )

        if not hasattr(
            application,
            "interview",
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Schedule an interview "
                        "before giving feedback."
                    )
                }
            )

        if not application.interview.recruiter_marked_done:
            raise ValidationError(
                {
                    "detail": (
                        "Mark the interview "
                        "as completed first."
                    )
                }
            )

        comments = (
            request.data.get(
                "comments"
            )
            or ""
        ).strip()

        reason_code = (
            request.data.get(
                "reason_code"
            )
            or ""
        ).strip()

        missing_skills = request.data.get(
            "missing_skills",
            [],
        )

        if not isinstance(
            missing_skills,
            list,
        ):
            raise ValidationError(
                {
                    "missing_skills": (
                        "Must be a list."
                    )
                }
            )

        feedback, _ = (
            Feedback.objects.update_or_create(
                application=application,
                defaults={
                    "reason_code": reason_code,
                    "comments": comments,
                    "missing_skills_json": (
                        missing_skills
                    ),
                    "is_system_generated": False,
                },
            )
        )

        application.status = (
            "feedback_given"
        )

        application.responded_at = (
            timezone.now()
        )

        application.save(
            update_fields=[
                "status",
                "responded_at",
            ]
        )

        return Response(
            {
                "detail": (
                    "Feedback submitted."
                ),

                "feedback": {
                    "id": feedback.id,

                    "reason_code": (
                        feedback.reason_code
                    ),

                    "comments": (
                        feedback.comments
                    ),

                    "missing_skills": (
                        feedback.missing_skills_json
                    ),
                },

                "application": (
                    application_payload(
                        application
                    )
                ),
            }
        )


class InterviewScheduleView(APIView):
    permission_classes = [
        IsRecruiter
    ]

    def post(self, request, pk):
        application = (
            Application.objects
            .select_related(
                "job__company",
                "seeker",
            )
            .filter(pk=pk)
            .first()
        )

        if not application:
            raise NotFound(
                "Application not found."
            )

        if (
            application.job.company.recruiter_user_id
            != request.user.id
        ):
            return Response(
                {
                    "detail": "Forbidden"
                },
                status=403,
            )

        if application.status not in (
            "shortlisted",
            "interview_scheduled",
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Only shortlisted "
                        "applications can "
                        "be scheduled "
                        "for interview."
                    )
                }
            )

        scheduled_at = request.data.get(
            "scheduled_at"
        )

        if not scheduled_at:
            raise ValidationError(
                {
                    "scheduled_at": (
                        "Required."
                    )
                }
            )

        mode = (
            request.data.get(
                "mode",
                "online",
            )
            or "online"
        )

        interview, created = (
            Interview.objects.update_or_create(
                application=application,
                defaults={
                    "scheduled_at": scheduled_at,
                    "mode": mode,
                    "recruiter_marked_done": False,
                    "seeker_confirmed": False,
                },
            )
        )

        application.status = (
            "interview_scheduled"
        )

        application.save(
            update_fields=[
                "status"
            ]
        )

        return Response(
            {
                "id": interview.id,

                "scheduled_at": (
                    interview.scheduled_at
                ),

                "mode": interview.mode,

                "seeker_confirmed": (
                    interview.seeker_confirmed
                ),
            }
        )


class InterviewDoneView(APIView):
    permission_classes = [
        IsRecruiter
    ]

    def post(self, request, pk):
        interview = (
            Interview.objects
            .select_related(
                "application__job__company"
            )
            .filter(pk=pk)
            .first()
        )

        if not interview:
            raise NotFound(
                "Interview not found."
            )

        if (
            interview
            .application
            .job
            .company
            .recruiter_user_id
            != request.user.id
        ):
            return Response(
                {
                    "detail": "Forbidden"
                },
                status=403,
            )

        interview.recruiter_marked_done = True

        interview.application.status = (
            "interview_completed"
        )

        interview.application.responded_at = (
            timezone.now()
        )

        interview.application.save(
            update_fields=[
                "status",
                "responded_at",
            ]
        )

        interview.save(
            update_fields=[
                "recruiter_marked_done"
            ]
        )

        return Response(
            {
                "status": "completed"
            }
        )


class InterviewConfirmView(APIView):
    permission_classes = [
        IsSeeker
    ]

    def post(self, request, pk):
        interview = (
            Interview.objects
            .select_related(
                "application__seeker"
            )
            .filter(pk=pk)
            .first()
        )

        if (
            not interview
            or interview.application.seeker.user_id
            != request.user.id
        ):
            return Response(
                {
                    "detail": (
                        "Interview not found."
                    )
                },
                status=404,
            )

        interview.seeker_confirmed = True

        interview.application.status = (
            "interview_scheduled"
        )

        interview.save(
            update_fields=[
                "seeker_confirmed"
            ]
        )

        interview.application.save(
            update_fields=[
                "status"
            ]
        )

        return Response(
            {
                "contact_unlocked": True
            }
        )


class CandidateSearchView(APIView):
    permission_classes = [
        IsRecruiter
    ]

    def get(self, request):
        from accounts.models import SeekerProfile

        queryset = (
            SeekerProfile.objects
            .select_related(
                "user",
                "campus",
            )
            .prefetch_related(
                "seeker_skills__skill"
            )
        )

        params = request.query_params

        if params.get("skills"):
            queryset = queryset.filter(
                seeker_skills__skill__name__icontains=(
                    params["skills"]
                )
            )

        if params.get("education"):
            queryset = queryset.filter(
                education__icontains=(
                    params["education"]
                )
            )

        if params.get("grad_year"):
            queryset = queryset.filter(
                grad_year=params["grad_year"]
            )

        if params.get("location"):
            queryset = queryset.filter(
                location__icontains=(
                    params["location"]
                )
            )

        if params.get("ats_min"):
            try:
                ats_min = int(
                    params["ats_min"]
                )
            except ValueError:
                raise ValidationError(
                    {
                        "ats_min": (
                            "Must be a number."
                        )
                    }
                )

            queryset = queryset.filter(
                ats_score__gte=ats_min
            )

        if params.get("experience"):
            queryset = queryset.filter(
                experience_level=(
                    params["experience"]
                )
            )

        if params.get("campus"):
            queryset = queryset.filter(
                campus__name__icontains=(
                    params["campus"]
                )
            )

        data = []

        for seeker in (
            queryset.distinct()[:100]
        ):
            data.append(
                {
                    "id": seeker.id,

                    "name": (
                        seeker.full_name
                        or seeker.user.full_name
                    ),

                    "email": seeker.user.email,

                    "skills": [
                        item.skill.name
                        for item in (
                            seeker.seeker_skills.all()
                        )
                    ],

                    "education": seeker.education,

                    "grad_year": seeker.grad_year,

                    "location": seeker.location,

                    "ats_score": seeker.ats_score,

                    "experience_level": (
                        seeker.experience_level
                    ),

                    "campus": (
                        seeker.campus.name
                        if seeker.campus
                        else None
                    ),
                }
            )

        return Response(data)


# ============================================================
# CONTACT UNLOCK PAYMENT
# ============================================================


class CreateContactUnlockOrderView(APIView):
    permission_classes = [
        IsRecruiter
    ]

    def post(self, request, pk):

        application = (
            Application.objects
            .select_related(
                "job__company"
            )
            .filter(pk=pk)
            .first()
        )

        if not application:
            raise NotFound(
                "Application not found."
            )

        if (
            application.job.company.recruiter_user_id
            != request.user.id
        ):
            return Response(
                {
                    "detail": "Forbidden"
                },
                status=403,
            )

        existing = getattr(
            application,
            "contact_unlock",
            None,
        )

        if (
            existing
            and existing.unlocked
        ):
            return Response(
                {
                    "unlocked": True,
                    "detail": (
                        "Contact is already unlocked."
                    ),
                }
            )

        amount = 99

        key_id = getattr(
            settings,
            "RAZORPAY_KEY_ID",
            "",
        )

        key_secret = getattr(
            settings,
            "RAZORPAY_KEY_SECRET",
            "",
        )

        if not key_id or not key_secret:
            return Response(
                {
                    "detail": (
                        "Razorpay test keys are not configured."
                    )
                },
                status=503,
            )

        try:
            import razorpay

            client = razorpay.Client(
                auth=(
                    key_id,
                    key_secret,
                )
            )

            order = client.order.create(
                {
                    "amount": amount * 100,
                    "currency": "INR",

                    "receipt": (
                        f"unlock-{request.user.id}-"
                        f"{application.id}-"
                        f"{int(timezone.now().timestamp())}"
                    ),

                    "notes": {
                        "user_id": str(
                            request.user.id
                        ),

                        "application_id": str(
                            application.id
                        ),
                    },
                }
            )

        except Exception:
            logger = __import__(
                "logging"
            ).getLogger(__name__)

            logger.exception(
                "Contact unlock Razorpay order creation failed."
            )

            return Response(
                {
                    "detail": (
                        "Could not create Razorpay order."
                    )
                },
                status=502,
            )

        unlock, _ = (
            ContactUnlock.objects.get_or_create(
                application=application,
                defaults={
                    "recruiter": request.user,
                    "amount": amount,
                },
            )
        )

        unlock.recruiter = request.user
        unlock.amount = amount
        unlock.razorpay_order_id = order["id"]

        unlock.save(
            update_fields=[
                "recruiter",
                "amount",
                "razorpay_order_id",
            ]
        )

        return Response(
            {
                "unlocked": False,
                "key_id": key_id,
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "application_id": application.id,
            },
            status=201,
        )


class VerifyContactUnlockPaymentView(APIView):
    permission_classes = [
        IsRecruiter
    ]

    def post(self, request, pk):

        application = (
            Application.objects
            .select_related(
                "job__company"
            )
            .filter(pk=pk)
            .first()
        )

        if not application:
            raise NotFound(
                "Application not found."
            )

        if (
            application.job.company.recruiter_user_id
            != request.user.id
        ):
            return Response(
                {
                    "detail": "Forbidden"
                },
                status=403,
            )

        unlock = (
            ContactUnlock.objects
            .filter(
                application=application,
                recruiter=request.user,
            )
            .first()
        )

        if not unlock:
            raise ValidationError(
                {
                    "detail": (
                        "Create an unlock order first."
                    )
                }
            )

        order_id = str(
            request.data.get(
                "razorpay_order_id",
                "",
            )
        ).strip()

        payment_id = str(
            request.data.get(
                "razorpay_payment_id",
                "",
            )
        ).strip()

        signature = str(
            request.data.get(
                "razorpay_signature",
                "",
            )
        ).strip()

        if (
            not order_id
            or not payment_id
            or not signature
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Razorpay payment details "
                        "are required."
                    )
                }
            )

        if (
            unlock.razorpay_order_id
            != order_id
        ):
            raise ValidationError(
                {
                    "detail": (
                        "Invalid Razorpay order."
                    )
                }
            )

        key_id = getattr(
            settings,
            "RAZORPAY_KEY_ID",
            "",
        )

        key_secret = getattr(
            settings,
            "RAZORPAY_KEY_SECRET",
            "",
        )

        if not key_id or not key_secret:
            return Response(
                {
                    "detail": (
                        "Razorpay test keys are not configured."
                    )
                },
                status=503,
            )

        try:
            import razorpay

            client = razorpay.Client(
                auth=(
                    key_id,
                    key_secret,
                )
            )

            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": order_id,
                    "razorpay_payment_id": payment_id,
                    "razorpay_signature": signature,
                }
            )

            order = client.order.fetch(
                order_id
            )

            expected_amount = int(
                unlock.amount * 100
            )

            notes = order.get(
                "notes"
            ) or {}

            if (
                str(order.get("amount"))
                != str(expected_amount)
                or str(
                    notes.get("user_id")
                )
                != str(request.user.id)
                or str(
                    notes.get("application_id")
                )
                != str(application.id)
            ):
                return Response(
                    {
                        "detail": (
                            "Payment does not match "
                            "this application."
                        )
                    },
                    status=400,
                )

        except Exception:
            logger = __import__(
                "logging"
            ).getLogger(__name__)

            logger.exception(
                "Contact unlock payment verification failed."
            )

            return Response(
                {
                    "detail": (
                        "Payment verification failed."
                    )
                },
                status=400,
            )

        unlock.unlocked = True

        unlock.razorpay_payment_id = (
            payment_id
        )

        unlock.razorpay_signature = (
            signature
        )

        unlock.unlocked_at = (
            timezone.now()
        )

        unlock.save(
            update_fields=[
                "unlocked",
                "razorpay_payment_id",
                "razorpay_signature",
                "unlocked_at",
            ]
        )

        return Response(
            {
                "unlocked": True,
                "detail": (
                    "Contact details unlocked successfully."
                ),
            }
        )