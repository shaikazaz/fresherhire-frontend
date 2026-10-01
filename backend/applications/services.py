from resumes.models import SeekerSkill

from .models import Application


def seeker_context(user):
    """Data the match score needs about the logged-in seeker, or None (not a seeker / no active resume)."""
    if not user.is_authenticated or user.role != "seeker":
        return None
    profile = getattr(user, "seeker_profile", None)
    if profile is None:
        return None
    resume = profile.resumes.filter(is_active=True).order_by("-uploaded_at").first()
    if resume is None:
        return None
    skills = {n.lower() for n in SeekerSkill.objects.filter(seeker=profile).values_list("skill__name", flat=True)}
    return {
        "profile": profile,
        "resume": resume,
        "skills": skills,
        "projects_text": resume.projects_text or resume.parsed_text,
        "ats": resume.ats_score,
        "education": profile.education,
        "grad_year": profile.grad_year,
        "location": profile.location,
        "open_to_relocate": profile.open_to_relocate,
    }


def job_to_dict(job):
    return {
        "title": job.title,
        "description": job.description,
        "location": job.location,
        "skills": [(js.skill.name, js.is_required) for js in job.job_skills.all()],
    }


def applied_map(user):
    """{job_id: status} for the logged-in seeker."""
    if not user.is_authenticated or user.role != "seeker":
        return {}
    profile = getattr(user, "seeker_profile", None)
    if profile is None:
        return {}
    return dict(Application.objects.filter(seeker=profile).values_list("job_id", "status"))
