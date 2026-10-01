from rest_framework import serializers

from .models import Job
from .services import set_job_skills, slots_left


class JobSerializer(serializers.ModelSerializer):
    """Read serializer. Optional context: matches {job_id: match dict}, applied {job_id: status}, detail bool."""

    company = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    slots_left = serializers.SerializerMethodField()
    applicants = serializers.SerializerMethodField()
    match_score = serializers.SerializerMethodField()
    eligible = serializers.SerializerMethodField()
    match = serializers.SerializerMethodField()
    application_status = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id", "slug", "title", "company", "description", "location", "job_type", "exp_level",
            "salary_min", "salary_max", "application_cap", "cap_mode", "min_match_score", "status",
            "jd_score", "created_at", "skills", "slots_left", "applicants", "match_score", "eligible",
            "match", "application_status",
        ]

    def get_company(self, obj):
        c = obj.company
        return {"id": c.id, "name": c.name, "is_verified": c.is_verified, "industry": c.industry,
                "website": c.website}

    def get_skills(self, obj):
        return [{"name": js.skill.name, "is_required": js.is_required} for js in obj.job_skills.all()]

    def get_slots_left(self, obj):
        return slots_left(obj)

    def get_applicants(self, obj):
        return getattr(obj, "total_apps", 0)

    def _match(self, obj):
        return self.context.get("matches", {}).get(obj.id)

    def get_match_score(self, obj):
        m = self._match(obj)
        return m["score"] if m else None

    def get_eligible(self, obj):
        m = self._match(obj)
        return (m["score"] >= obj.min_match_score) if m else None

    def get_match(self, obj):
        return self._match(obj) if self.context.get("detail") else None

    def get_application_status(self, obj):
        return self.context.get("applied", {}).get(obj.id)


class JobCreateSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(child=serializers.CharField(max_length=80), required=False, allow_empty=True)

    class Meta:
        model = Job
        fields = ["title", "description", "location", "job_type", "exp_level", "salary_min", "salary_max",
                  "application_cap", "cap_mode", "min_match_score", "skills"]

    def validate_application_cap(self, value):
        if not 1 <= value <= 1000:
            raise serializers.ValidationError("Application cap must be between 1 and 1000.")
        return value

    def validate_min_match_score(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Minimum match score must be between 0 and 100.")
        return value

    def validate(self, attrs):
        lo, hi = attrs.get("salary_min"), attrs.get("salary_max")
        if lo and hi and lo > hi:
            raise serializers.ValidationError({"salary_max": "Maximum salary must be at least the minimum."})
        return attrs

    def create(self, validated):
        from datetime import timedelta
        from django.utils import timezone

        skills = validated.pop("skills", [])
        job = Job.objects.create(company=self.context["company"], **validated)
        if job.cap_mode == "best_match_window":
            job.review_window_ends_at = timezone.now() + timedelta(hours=24)
            job.save(update_fields=["review_window_ends_at", "updated_at"])
        set_job_skills(job, skills)
        return job
