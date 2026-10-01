
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, ExpressionWrapper, F, DurationField

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Company
from .permissions import IsPlatformAdmin
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


def auth_payload(user):
    """
    Create JWT tokens and return logged-in user information.
    """

    refresh = RefreshToken.for_user(user)

    refresh["role"] = user.role
    refresh["email"] = user.email

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": UserSerializer(user).data,
    }


class LoginView(TokenObtainPairView):
    """
    Login endpoint.
    """

    serializer_class = LoginSerializer


class RegisterView(APIView):
    """
    Public registration endpoint.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            auth_payload(user),
            status=201,
        )


class MeView(APIView):
    """
    Return the currently logged-in user.
    """

    def get(self, request):
        return Response(
            UserSerializer(request.user).data
        )


class PlatformStatsView(APIView):
    """
    Basic platform statistics for platform admins.
    """

    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        from applications.models import Application
        from jobs.models import Job

        return Response(
            {
                "seekers": User.objects.filter(
                    role="seeker"
                ).count(),

                "recruiters": User.objects.filter(
                    role="recruiter"
                ).count(),

                "companies": Company.objects.count(),

                "unverified_companies": Company.objects.filter(
                    is_verified=False
                ).count(),

                "active_jobs": Job.objects.filter(
                    status="active"
                ).count(),

                "applications": Application.objects.count(),

                "placements": Application.objects.filter(
                    status__in=["offered", "placed"]
                ).count(),
            }
        )


class AdminAnalyticsView(APIView):
    """
    Detailed analytics for platform admins.
    """

    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        from applications.models import Application
        from billing.models import Subscription
        from jobs.models import Job
        from notifications.models import Notification

        # ---------------------------------------------------------
        # Application status counts
        # ---------------------------------------------------------

        status_rows = list(
            Application.objects
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        # ---------------------------------------------------------
        # Top jobs by number of applications
        # ---------------------------------------------------------

        top_jobs = list(
            Job.objects
            .annotate(
                applications_count=Count("applications")
            )
            .values(
                "id",
                "title",
                "status",
                "applications_count",
            )
            .order_by(
                "-applications_count",
                "-created_at",
            )[:10]
        )

        # ---------------------------------------------------------
        # Average response time
        # ---------------------------------------------------------

        avg_hours = None

        # Only calculate this if the Application model
        # actually contains these fields.
        try:
            response_metrics = Application.objects.filter(
                responded_at__isnull=False,
                applied_at__isnull=False,
            )

            if response_metrics.exists():
                total_seconds = 0

                for application in response_metrics.only(
                    "applied_at",
                    "responded_at",
                ):
                    if (
                        application.applied_at
                        and application.responded_at
                    ):
                        seconds = (
                            application.responded_at
                            - application.applied_at
                        ).total_seconds()

                        total_seconds += max(0, seconds)

                count = response_metrics.count()

                if count > 0:
                    avg_hours = round(
                        total_seconds / count / 3600,
                        2,
                    )

        except Exception:
            # If these fields do not exist in the current
            # Application model, don't crash the entire
            # admin analytics endpoint.
            avg_hours = None

        # ---------------------------------------------------------
        # Return analytics
        # ---------------------------------------------------------

        return Response(
            {
                "users": {
                    "seekers": User.objects.filter(
                        role="seeker"
                    ).count(),

                    "recruiters": User.objects.filter(
                        role="recruiter"
                    ).count(),

                    "admins": User.objects.filter(
                        role="admin"
                    ).count(),
                },

                "jobs": {
                    "active": Job.objects.filter(
                        status="active"
                    ).count(),

                    "draft": Job.objects.filter(
                        status="draft"
                    ).count(),

                    "pending": Job.objects.filter(
                        status="pending"
                    ).count(),

                    "closed": Job.objects.filter(
                        status="closed"
                    ).count(),
                },

                "applications_by_status": status_rows,

                "average_response_hours": avg_hours,

                "active_subscriptions": Subscription.objects.filter(
                    status="active"
                ).count(),

                "notifications": Notification.objects.count(),

                "top_jobs": top_jobs,
            }
        )
