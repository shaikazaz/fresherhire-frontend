from datetime import timedelta
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Plan, Subscription


logger = logging.getLogger(__name__)


def activate_subscription(
    user,
    plan,
    order_id="",
    payment_id="",
    signature="",
):
    now = timezone.now()

    with transaction.atomic():

        Subscription.objects.filter(
            user=user,
            status="active",
        ).update(
            status="expired",
            end=now,
        )

        return Subscription.objects.create(
            user=user,
            plan=plan,
            start=now,
            end=now + timedelta(days=30),
            status="active",
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            razorpay_signature=signature,
        )


class PlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        plans = (
            Plan.objects
            .filter(is_active=True)
            .order_by("price")
        )

        return Response([
            {
                "id": plan.id,
                "name": plan.name,
                "price": plan.price,
                "application_limit": plan.application_limit,
                "profile_boost": plan.profile_boost,
                "priority_applications": plan.priority_applications,
                "resume_review": plan.resume_review,
                "features": plan.features_json,
            }
            for plan in plans
        ])


class CurrentPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        subscription = (
            Subscription.objects
            .filter(
                user=request.user,
                status="active",
            )
            .select_related("plan")
            .order_by("-start")
            .first()
        )

        if (
            subscription
            and subscription.end
            and subscription.end < timezone.now()
        ):
            subscription.status = "expired"
            subscription.save(update_fields=["status"])
            subscription = None

        if subscription:

            return Response({
                "plan": subscription.plan.name,
                "application_limit": subscription.plan.application_limit,
                "profile_boost": subscription.plan.profile_boost,
                "priority_applications": (
                    subscription.plan.priority_applications
                ),
                "resume_review": subscription.plan.resume_review,
                "subscription_id": subscription.id,
                "end": subscription.end,
                "payment_id": subscription.razorpay_payment_id,
            })

        return Response({
            "plan": "Free",
            "application_limit": 5,
            "profile_boost": False,
            "priority_applications": False,
            "resume_review": False,
            "subscription_id": None,
            "end": None,
            "payment_id": "",
        })


class ActivatePlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        plan = (
            Plan.objects
            .filter(
                pk=request.data.get("plan_id"),
                is_active=True,
            )
            .first()
        )

        if not plan:
            return Response(
                {"detail": "Plan not found."},
                status=404,
            )

        if (
            plan.price > 0
            and not getattr(
                settings,
                "RAZORPAY_ALLOW_DIRECT_ACTIVATION",
                False,
            )
        ):
            return Response(
                {
                    "detail": (
                        "Paid plans must be activated "
                        "through Razorpay."
                    )
                },
                status=402,
            )

        subscription = activate_subscription(
            request.user,
            plan,
        )

        return Response({
            "plan": plan.name,
            "application_limit": plan.application_limit,
            "subscription_id": subscription.id,
            "end": subscription.end,
        })


class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        plan = (
            Plan.objects
            .filter(
                pk=request.data.get("plan_id"),
                is_active=True,
            )
            .first()
        )

        if not plan:
            return Response(
                {"detail": "Plan not found."},
                status=404,
            )

        # Free plan
        if plan.price <= 0:

            subscription = activate_subscription(
                request.user,
                plan,
            )

            return Response({
                "free": True,
                "plan": plan.name,
                "application_limit": plan.application_limit,
                "subscription_id": subscription.id,
            })

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

            amount = int(
                round(float(plan.price) * 100)
            )

            receipt = (
                f"fh-user-{request.user.id}-"
                f"{plan.id}-"
                f"{int(timezone.now().timestamp())}"
            )

            order_data = {
                "amount": amount,
                "currency": "INR",
                "receipt": receipt,
                "notes": {
                    "user_id": str(request.user.id),
                    "plan_id": str(plan.id),
                },
            }

            order = client.order.create(
                order_data
            )

        except Exception as exc:

            logger.exception(
                "Razorpay order creation failed: %s",
                exc,
            )

            return Response(
                {
                    "detail": (
                        "Could not create Razorpay test order."
                    )
                },
                status=502,
            )

        return Response(
            {
                "key_id": key_id,
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "plan_id": plan.id,
                "plan_name": plan.name,
            },
            status=201,
        )


class VerifyRazorpayPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        plan = (
            Plan.objects
            .filter(
                pk=request.data.get("plan_id"),
                is_active=True,
            )
            .first()
        )

        if not plan:
            return Response(
                {"detail": "Plan not found."},
                status=404,
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

        if not order_id or not payment_id or not signature:

            raise ValidationError({
                "detail": (
                    "Razorpay payment details "
                    "are required."
                )
            })

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

            # Verify signature
            client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            })

            # Fetch order
            order = client.order.fetch(
                order_id
            )

            expected_amount = int(
                round(float(plan.price) * 100)
            )

            notes = order.get("notes") or {}

            if (
                str(order.get("amount"))
                != str(expected_amount)
                or str(notes.get("user_id"))
                != str(request.user.id)
                or str(notes.get("plan_id"))
                != str(plan.id)
            ):

                return Response(
                    {
                        "detail": (
                            "Razorpay order does not "
                            "match this user and plan."
                        )
                    },
                    status=400,
                )

        except Exception as exc:

            logger.exception(
                "Razorpay verification failed: %s",
                exc,
            )

            return Response(
                {
                    "detail": (
                        "Payment signature verification failed."
                    )
                },
                status=400,
            )

        subscription = activate_subscription(
            request.user,
            plan,
            order_id,
            payment_id,
            signature,
        )

        return Response({
            "detail": (
                "Payment verified and "
                "membership activated."
            ),
            "plan": plan.name,
            "application_limit": plan.application_limit,
            "subscription_id": subscription.id,
            "end": subscription.end,
        })