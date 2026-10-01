import math

from django.db import transaction
from django.utils import timezone

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsRecruiter
from applications.match import compute_match
from applications.services import (
    applied_map,
    job_to_dict,
    seeker_context,
)
from billing.models import Plan

from notifications.services import notify_matching_seekers

from .models import (
    SLOT_STATUSES,
    Skill,
    Job,
)
from .serializers import (
    JobCreateSerializer,
    JobSerializer,
)
from .services import (
    apply_filters,
    base_queryset,
    slots_left,
)


PAGE_SIZE = 12


def current_plan(company):
    """
    Get the active subscription plan for the recruiter
    who owns this company.
    """

    if company is None:
        return Plan.objects.filter(
            name="Free",
            is_active=True,
        ).first()

    recruiter = getattr(
        company,
        "recruiter_user",
        None,
    )

    if recruiter is None:
        return Plan.objects.filter(
            name="Free",
            is_active=True,
        ).first()

    subscription = (
        recruiter.subscriptions
        .filter(status="active")
        .select_related("plan")
        .order_by("-start")
        .first()
    )

    if subscription:
        if (
            subscription.end is None
            or subscription.end >= timezone.now()
        ):
            return subscription.plan

        subscription.status = "expired"
        subscription.save(
            update_fields=["status"]
        )

    return Plan.objects.filter(
        name="Free",
        is_active=True,
    ).first()


class JobListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsRecruiter()]

        return [AllowAny()]

    def get(self, request):
        params = request.query_params

        queryset = apply_filters(
            base_queryset().filter(
                status="active"
            ),
            params,
        )

        sort = params.get("sort", "")

        if sort == "salary":
            queryset = queryset.order_by(
                "-salary_max",
                "-created_at",
            )
        else:
            queryset = queryset.order_by(
                "-created_at"
            )

        jobs = list(queryset)

        context = seeker_context(
            request.user
        )

        matches = {}

        if context:
            matches = {
                job.id: compute_match(
                    context,
                    job_to_dict(job),
                )
                for job in jobs
            }

            if sort in ("", "match"):
                jobs.sort(
                    key=lambda job: (
                        slots_left(job) == 0,
                        -matches[job.id]["score"],
                        -job.created_at.timestamp(),
                        slots_left(job),
                    )
                )

        try:
            page = max(
                1,
                int(params.get("page", 1)),
            )
        except (TypeError, ValueError):
            page = 1

        total = len(jobs)

        pages = max(
            1,
            math.ceil(
                total / PAGE_SIZE
            ),
        )

        page = min(
            page,
            pages,
        )

        start = (page - 1) * PAGE_SIZE
        end = page * PAGE_SIZE

        chunk = jobs[start:end]

        data = JobSerializer(
            chunk,
            many=True,
            context={
                "matches": matches,
                "applied": applied_map(
                    request.user
                ),
            },
        ).data

        return Response(
            {
                "count": total,
                "page": page,
                "total_pages": pages,
                "is_seeker": (
                    request.user.is_authenticated
                    and request.user.role == "seeker"
                ),
                "has_resume": context is not None,
                "results": data,
            }
        )

    def post(self, request):

        company = getattr(
            request.user,
            "company",
            None,
        )

        if company is None:
            raise ValidationError(
                {
                    "detail": (
                        "Your account has no "
                        "company profile."
                    )
                }
            )

        plan = current_plan(company)

        active_jobs = Job.objects.filter(
            company=company,
            status__in=[
                "active",
                "pending",
                "draft",
            ],
        ).count()

        if (
            plan
            and active_jobs >= plan.job_limit
        ):
            return Response(
                {
                    "detail": (
                        f"Your {plan.name} plan "
                        f"allows {plan.job_limit} "
                        "active job(s). "
                        "Upgrade your plan to "
                        "post another job."
                    )
                },
                status=402,
            )

        serializer = JobCreateSerializer(
            data=request.data,
            context={
                "company": company,
            },
        )

        serializer.is_valid(
            raise_exception=True
        )

        job = serializer.save()

        job = (
            base_queryset()
            .get(pk=job.pk)
        )

        notify_matching_seekers(job)

        return Response(
            JobSerializer(
                job,
                context={
                    "detail": True,
                },
            ).data,
            status=201,
        )


class JobDetailView(APIView):

    permission_classes = [
        AllowAny
    ]

    def get(self, request, slug):

        job = (
            base_queryset()
            .filter(slug=slug)
            .first()
        )

        if job is None:
            raise NotFound(
                "Job not found."
            )

        if job.status in (
            "draft",
            "pending",
        ):
            user = request.user

            owner = (
                user.is_authenticated
                and (
                    job.company.recruiter_user_id
                    == user.id
                    or user.role == "admin"
                )
            )

            if not owner:
                raise NotFound(
                    "Job not found."
                )

        context = seeker_context(
            request.user
        )

        matches = {}

        if context:
            matches = {
                job.id: compute_match(
                    context,
                    job_to_dict(job),
                )
            }

        data = dict(
            JobSerializer(
                job,
                context={
                    "matches": matches,
                    "applied": applied_map(
                        request.user
                    ),
                    "detail": True,
                },
            ).data
        )

        data["viewer"] = {
            "is_seeker": (
                request.user.is_authenticated
                and request.user.role == "seeker"
            ),
            "has_resume": context is not None,
        }

        return Response(data)

    def patch(self, request, slug):

        job = (
            base_queryset()
            .filter(slug=slug)
            .first()
        )

        if not job:
            raise NotFound(
                "Job not found."
            )

        is_owner = (
            request.user.role == "admin"
            or job.company.recruiter_user_id
            == request.user.id
        )

        if not is_owner:
            return Response(
                {
                    "detail": "Forbidden"
                },
                status=403,
            )

        allowed_fields = {
            "title",
            "description",
            "location",
            "job_type",
            "exp_level",
            "salary_min",
            "salary_max",
            "application_cap",
            "cap_mode",
            "min_match_score",
            "status",
        }

        for key, value in request.data.items():
            if key in allowed_fields:
                setattr(
                    job,
                    key,
                    value,
                )

        job.save()

        return Response(
            JobSerializer(job).data
        )


class MyJobsView(APIView):

    permission_classes = [
        IsRecruiter
    ]

    def get(self, request):

        company = getattr(
            request.user,
            "company",
            None,
        )

        if company:
            jobs = (
                base_queryset()
                .filter(company=company)
                .order_by("-created_at")
            )
        else:
            jobs = Job.objects.none()

        return Response(
            JobSerializer(
                jobs,
                many=True,
            ).data
        )


class ExtendCapView(APIView):

    permission_classes = [
        IsRecruiter
    ]

    def post(self, request, pk):

        job = (
            base_queryset()
            .filter(
                pk=pk,
                company__recruiter_user=request.user,
            )
            .first()
        )

        if not job:
            raise NotFound(
                "Job not found."
            )

        try:
            additional_slots = int(
                request.data.get(
                    "additional_slots",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            raise ValidationError(
                {
                    "additional_slots": (
                        "Must be a valid number."
                    )
                }
            )

        if additional_slots < 1:
            raise ValidationError(
                {
                    "additional_slots": (
                        "Must be at least 1."
                    )
                }
            )

        with transaction.atomic():

            job = (
                Job.objects
                .select_for_update()
                .get(pk=job.pk)
            )

            job.application_cap += (
                additional_slots
            )

            job.extended_count += 1

            job.save(
                update_fields=[
                    "application_cap",
                    "extended_count",
                    "updated_at",
                ]
            )

            from applications.models import Application

            waitlisted = list(
                Application.objects.filter(
                    job=job,
                    status="waitlisted",
                )
                .order_by(
                    "-match_score",
                    "applied_at",
                )[
                    :additional_slots
                ]
            )

            promoted_ids = []

            for application in waitlisted:

                application.status = "applied"

                application.save(
                    update_fields=[
                        "status"
                    ]
                )

                promoted_ids.append(
                    application.id
                )

        return Response(
            {
                "application_cap": (
                    job.application_cap
                ),
                "promoted_application_ids": (
                    promoted_ids
                ),
            }
        )


class FinalizeBestMatchWindowView(APIView):

    permission_classes = [
        IsRecruiter
    ]

    def post(self, request, pk):

        job = (
            base_queryset()
            .filter(
                pk=pk,
                company__recruiter_user=request.user,
            )
            .first()
        )

        if not job:
            raise NotFound(
                "Job not found."
            )

        if job.cap_mode != "best_match_window":
            raise ValidationError(
                {
                    "detail": (
                        "This job is not using "
                        "best-match window mode."
                    )
                }
            )

        from applications.models import Application

        with transaction.atomic():

            job = (
                Job.objects
                .select_for_update()
                .get(pk=job.pk)
            )

            waiting = list(
                Application.objects.filter(
                    job=job,
                    status="waitlisted",
                )
                .order_by(
                    "-match_score",
                    "applied_at",
                )
            )

            used_slots = (
                Application.objects.filter(
                    job=job,
                    status__in=SLOT_STATUSES,
                ).count()
            )

            open_slots = max(
                0,
                job.application_cap
                - used_slots,
            )

            promoted_ids = []

            for application in waiting[
                :open_slots
            ]:
                application.status = "applied"

                application.save(
                    update_fields=[
                        "status"
                    ]
                )

                promoted_ids.append(
                    application.id
                )

            job.review_window_ends_at = None

            job.save(
                update_fields=[
                    "review_window_ends_at",
                    "updated_at",
                ]
            )

        return Response(
            {
                "promoted_application_ids": (
                    promoted_ids
                )
            }
        )


class RecruiterDashboardView(APIView):

    permission_classes = [
        IsRecruiter
    ]

    def get(self, request):

        company = getattr(
            request.user,
            "company",
            None,
        )

        if company:
            jobs = list(
                base_queryset()
                .filter(company=company)
                .order_by("-created_at")
            )
        else:
            jobs = []

        return Response(
            {
                "company": (
                    {
                        "name": company.name,
                        "is_verified": (
                            company.is_verified
                        ),
                    }
                    if company
                    else None
                ),
                "active_jobs": sum(
                    1
                    for job in jobs
                    if job.status == "active"
                ),
                "closed_jobs": sum(
                    1
                    for job in jobs
                    if job.status == "closed"
                ),
                "total_applicants": sum(
                    getattr(
                        job,
                        "total_apps",
                        0,
                    )
                    for job in jobs
                ),
                "jobs": JobSerializer(
                    jobs[:10],
                    many=True,
                ).data,
            }
        )


class SkillListView(APIView):

    permission_classes = [
        AllowAny
    ]

    authentication_classes = []

    def get(self, request):

        return Response(
            list(
                Skill.objects.values_list(
                    "name",
                    flat=True,
                )
            )
        )