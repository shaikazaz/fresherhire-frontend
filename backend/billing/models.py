from django.conf import settings
from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    # Candidate benefits
    application_limit = models.PositiveIntegerField(default=5)
    profile_boost = models.BooleanField(default=False)
    priority_applications = models.BooleanField(default=False)
    resume_review = models.BooleanField(default=False)

    # Recruiter benefits
    job_limit = models.PositiveIntegerField(default=1)

    features_json = models.JSONField(
        default=dict,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUSES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )

    start = models.DateTimeField()

    end = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default="active",
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f"{self.user_id} - {self.plan.name}"