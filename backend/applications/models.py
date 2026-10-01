from django.db import models


class Application(models.Model):
    STATUSES = [
        ("applied", "Applied"),
        ("waitlisted", "Waitlisted"),
        ("shortlisted", "Shortlisted"),
        ("interview_scheduled", "Interview scheduled"),
        ("interview_completed", "Interview completed"),
        ("feedback_given", "Feedback given"),
        ("offered", "Offered"),
        ("placed", "Placed"),
        ("rejected", "Rejected"),
        ("withdrawn", "Withdrawn"),
    ]

    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE,
        related_name="applications",
    )

    seeker = models.ForeignKey(
        "accounts.SeekerProfile",
        on_delete=models.CASCADE,
        related_name="applications",
    )

    resume = models.ForeignKey(
        "resumes.Resume",
        null=True,
        on_delete=models.SET_NULL,
        related_name="applications",
    )

    match_score = models.PositiveSmallIntegerField(default=0)

    status = models.CharField(
        max_length=25,
        choices=STATUSES,
        default="applied",
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    response_due_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    responded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ("job", "seeker")
        ordering = ["-applied_at"]

    def __str__(self):
        return "%s -> %s (%s)" % (
            self.seeker_id,
            self.job_id,
            self.status,
        )


class ContactUnlock(models.Model):
    """
    Records a recruiter payment that unlocks contact
    information for one specific application.
    """

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="contact_unlock",
    )

    recruiter = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="contact_unlocks",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=99,
    )

    unlocked = models.BooleanField(
        default=False,
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

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"Application {self.application_id} - "
            f"Recruiter {self.recruiter_id} - "
            f"Unlocked: {self.unlocked}"
        )


class Interview(models.Model):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="interview",
    )

    scheduled_at = models.DateTimeField()

    mode = models.CharField(
        max_length=30,
        default="online",
    )

    recruiter_marked_done = models.BooleanField(
        default=False,
    )

    seeker_confirmed = models.BooleanField(
        default=False,
    )


class Feedback(models.Model):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="feedback",
    )

    reason_code = models.CharField(
        max_length=50,
        blank=True,
    )

    comments = models.TextField(
        blank=True,
    )

    is_system_generated = models.BooleanField(
        default=False,
    )

    missing_skills_json = models.JSONField(
        default=list,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )