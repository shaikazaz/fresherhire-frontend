from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsSeeker
from jobs.models import Job, JobSkill
from resumes.models import SeekerSkill

from .models import SkillResource


class CareerGuideView(APIView):
    permission_classes = [IsSeeker]

    def get(self, request):
        profile = request.user.seeker_profile
        have = {n.lower() for n in SeekerSkill.objects.filter(seeker=profile).values_list("skill__name", flat=True)}

        jobs = Job.objects.filter(status="active")
        role = (request.query_params.get("role") or "").strip()
        if role:
            jobs = jobs.filter(title__icontains=role)
        total_jobs = jobs.count()

        rows = list(
            JobSkill.objects.filter(job__in=jobs, is_required=True)
            .values("skill_id", "skill__name")
            .annotate(n=Count("job_id", distinct=True))
            .order_by("-n", "skill__name")
        )

        def pct(n):
            return round(100 * n / total_jobs) if total_jobs else 0

        gaps = [r for r in rows if r["skill__name"].lower() not in have][:10]
        resources = {}
        for res in SkillResource.objects.filter(skill_id__in=[g["skill_id"] for g in gaps]):
            resources.setdefault(res.skill_id, []).append(
                {"kind": res.kind, "title": res.title, "url": res.url, "provider": res.provider})

        gap_data = [{
            "skill": g["skill__name"], "demand_jobs": g["n"], "demand_pct": pct(g["n"]),
            "resources": resources.get(g["skill_id"], []),
        } for g in gaps]
        projects = [r for g in gap_data[:5] for r in g["resources"] if r["kind"] == "project"][:4]

        resume = profile.resumes.filter(is_active=True).first() or profile.resumes.first()
        return Response({
            "total_jobs": total_jobs,
            "role": role,
            "skills_have": sorted(have),
            "gaps": gap_data,
            "project_ideas": projects,
            "market_top": [{"skill": r["skill__name"], "demand_pct": pct(r["n"]),
                            "you_have": r["skill__name"].lower() in have} for r in rows[:8]],
            "resume_fixes": (resume.ats_report.get("fixes", []) if resume else []),
            "has_resume": resume is not None,
            "ats_score": resume.ats_score if resume else 0,
        })
