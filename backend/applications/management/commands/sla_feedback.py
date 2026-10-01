from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from applications.models import Application, Feedback


class Command(BaseCommand):
    help = "Create automatic system feedback for applications that missed the response SLA."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Report overdue applications without creating feedback.")

    def handle(self, *args, **options):
        now = timezone.now()
        qs = Application.objects.filter(
            response_due_at__isnull=False,
            response_due_at__lt=now,
            responded_at__isnull=True,
        ).exclude(status__in=["withdrawn", "rejected", "placed"])
        count = 0
        for app in qs.select_related("job"):
            if Feedback.objects.filter(application=app).exists():
                continue
            if options["dry_run"]:
                self.stdout.write(f"OVERDUE application={app.id} job={app.job.title}")
                count += 1
                continue
            with transaction.atomic():
                Feedback.objects.create(
                    application=app,
                    reason_code="sla_missed",
                    comments=f"The recruiter response SLA of {app.job.response_sla_days} day(s) was missed. FresherHire generated this system feedback automatically.",
                    is_system_generated=True,
                )
                app.status = "feedback_given"
                app.responded_at = now
                app.save(update_fields=["status", "responded_at"])
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {count} overdue application(s)."))
