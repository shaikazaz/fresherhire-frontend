from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError

from applications.match import compute_match
from applications.services import job_to_dict, seeker_context
from accounts.models import SeekerProfile

from .models import Notification


def notify_matching_seekers(job):
    created = 0
    emailed = 0

    profiles = (
        SeekerProfile.objects
        .select_related("user")
        .prefetch_related(
            "seeker_skills__skill",
            "resumes",
        )
    )

    job_data = job_to_dict(job)

    for profile in profiles:
        # Only notify active seeker accounts.
        if profile.user.role != "seeker" or not profile.user.is_active:
            continue

        # Build seeker matching context.
        ctx = seeker_context(profile.user)

        # If there is no resume/profile context, create a basic
        # context from the seeker profile instead of skipping them.
        if not ctx:
            ctx = {
                "skills": [],
                "experience_level": profile.experience_level or "",
                "location": profile.location or "",
                "education": profile.education or "",
                "resume_text": "",
            }

        # Calculate the match score.
        result = compute_match(ctx, job_data)
        score = result["score"]

        # Respect the job's minimum match requirement.
        if score < job.min_match_score:
            continue

        # Prevent duplicate notifications for the same job/seeker.
        key = f"job:{job.id}:seeker:{profile.user_id}"

        try:
            Notification.objects.create(
                user=profile.user,
                message=f"New matching job: {job.title} ({score}% match)",
                link=f"/jobs/{job.slug}",
                notification_type="matching_job",
                event_key=key,
            )
            created += 1

        except IntegrityError:
            # Notification already exists.
            continue

        # Send email notification.
        send_mail(
            subject=f"FresherHire: {job.title} may be a match for you",
            message=(
                f"A new job matches your profile at {score}%. "
                f"View it: /jobs/{job.slug}"
            ),
            from_email=getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                "FresherHire <no-reply@localhost>",
            ),
            recipient_list=[profile.user.email],
            fail_silently=True,
        )

        emailed += 1

    return {
        "notifications": created,
        "emails_attempted": emailed,
    }