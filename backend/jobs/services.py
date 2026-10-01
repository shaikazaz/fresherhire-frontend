from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from .models import SLOT_STATUSES, Job, JobSkill, Skill


def base_queryset():
    """Jobs with company, skills and application counts pre-loaded."""
    return (
        Job.objects.select_related("company")
        .prefetch_related("job_skills__skill")
        .annotate(
            active_apps=Count("applications", filter=Q(applications__status__in=SLOT_STATUSES), distinct=True),
            total_apps=Count("applications", distinct=True),
        )
    )


def slots_left(job):
    return max(0, job.application_cap - getattr(job, "active_apps", 0))


def apply_filters(qs, params):
    q = (params.get("q") or "").strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(company__name__icontains=q) | Q(description__icontains=q))

    location = (params.get("location") or "").strip()
    if location:
        qs = qs.filter(location__icontains=location)

    job_type = params.get("job_type")
    if job_type in dict(Job.JOB_TYPES):
        qs = qs.filter(job_type=job_type)

    exp_level = params.get("exp_level")
    if exp_level in dict(Job.EXP_LEVELS):
        qs = qs.filter(exp_level=exp_level)

    names = [s.strip() for s in (params.get("skills") or "").split(",") if s.strip()]
    if names:
        cond = Q()
        for name in names:
            cond |= Q(skill__name__iexact=name)
        qs = qs.filter(id__in=JobSkill.objects.filter(cond).values("job_id"))

    try:
        salary_min = int(params.get("salary_min") or 0)
    except ValueError:
        salary_min = 0
    if salary_min > 0:
        qs = qs.filter(salary_max__gte=salary_min)

    try:
        days = int(params.get("posted") or 0)
    except ValueError:
        days = 0
    if days in (1, 3, 7, 30):
        qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=days))
    return qs


def set_job_skills(job, names, required=True):
    for raw in names:
        name = str(raw).strip()[:80]
        if not name:
            continue
        skill = Skill.objects.filter(name__iexact=name).first() or Skill.objects.create(name=name)
        JobSkill.objects.get_or_create(job=job, skill=skill, defaults={"is_required": required})
