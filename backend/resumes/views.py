
import io
import logging
import os

from django.conf import settings
from django.db import transaction

from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import SeekerProfile
from accounts.permissions import IsSeeker
from jobs.models import Skill

from .ats import scan
from .models import Resume, SeekerSkill
from .parser import extract_profile, extract_text


logger = logging.getLogger(__name__)


SIGNATURES = {
    "pdf": b"%PDF",
    "docx": b"PK",
}


def resume_payload(resume, request=None):
    url = ""

    if resume.file:
        url = resume.file.url

        if request is not None:
            url = request.build_absolute_uri(url)

    return {
        "id": resume.id,
        "original_name": resume.original_name,
        "ats_score": resume.ats_score,
        "passed": resume.passed,
        "is_active": resume.is_active,
        "threshold": settings.ATS_PASS_SCORE,
        "report": resume.ats_report,
        "uploaded_at": resume.uploaded_at,
        "file_url": url,
    }


def activate_resume(profile, resume, report, info):
    """
    Make this resume the active resume.

    When a new resume passes the ATS check, update the
    seeker's profile using information extracted from
    the NEW resume.

    Updated automatically:
    - Full name
    - Phone
    - Education
    - Graduation year
    - Location
    - Experience level
    - Resume-based skills
    - ATS score
    """

    # ---------------------------------------------------------
    # 1. Deactivate all previous resumes
    # ---------------------------------------------------------

    profile.resumes.exclude(
        pk=resume.pk
    ).update(
        is_active=False
    )

    # ---------------------------------------------------------
    # 2. Activate the new resume
    # ---------------------------------------------------------

    resume.is_active = True
    resume.save(
        update_fields=["is_active"]
    )

    # ---------------------------------------------------------
    # 3. Update ATS score
    # ---------------------------------------------------------

    profile.ats_score = report.get(
        "score",
        0
    )

    # ---------------------------------------------------------
    # 4. Update full name from NEW resume
    # ---------------------------------------------------------

    full_name = info.get(
        "full_name"
    )

    if full_name:
        full_name = str(
            full_name
        ).strip()

        if full_name:
            full_name = full_name[:150]

            profile.full_name = full_name

            # Keep User full name synchronized
            profile.user.full_name = full_name

    # ---------------------------------------------------------
    # 5. Update phone from NEW resume
    # ---------------------------------------------------------

    phone = info.get(
        "phone"
    )

    if phone:
        phone = str(
            phone
        ).strip()

        if phone:
            profile.phone = phone[:30]

    # ---------------------------------------------------------
    # 6. Update education from NEW resume
    # ---------------------------------------------------------

    education = info.get(
        "education"
    )

    if education:
        education = str(
            education
        ).strip()

        if education:
            profile.education = education[:200]

    # ---------------------------------------------------------
    # 7. Update graduation year from NEW resume
    # ---------------------------------------------------------

    grad_year = info.get(
        "grad_year"
    )

    if grad_year not in (
        None,
        "",
    ):
        try:
            grad_year = int(
                grad_year
            )

            if 1990 <= grad_year <= 2040:
                profile.grad_year = grad_year

        except (
            TypeError,
            ValueError,
        ):
            logger.warning(
                "Invalid graduation year extracted from resume: %s",
                grad_year,
            )

    # ---------------------------------------------------------
    # 8. Update location from NEW resume
    # ---------------------------------------------------------

    location = info.get(
        "location"
    )

    if location:
        location = str(
            location
        ).strip()

        if location:
            profile.location = location[:120]

    # ---------------------------------------------------------
    # 9. Update experience level from NEW resume
    # ---------------------------------------------------------

    experience_level = info.get(
        "experience_level"
    )

    if experience_level:
        experience_level = str(
            experience_level
        ).strip().lower()

        valid_levels = dict(
            SeekerProfile.EXP_LEVELS
        )

        if experience_level in valid_levels:
            profile.experience_level = (
                experience_level
            )

    # ---------------------------------------------------------
    # 10. Save seeker profile
    # ---------------------------------------------------------

    profile.save()

    # Save User full name if it was extracted
    if full_name:
        profile.user.save(
            update_fields=["full_name"]
        )

    # ---------------------------------------------------------
    # 11. Remove skills from previous resume
    # ---------------------------------------------------------

    SeekerSkill.objects.filter(
        seeker=profile,
        source="resume",
    ).delete()

    # ---------------------------------------------------------
    # 12. Add skills from NEW resume
    # ---------------------------------------------------------

    skills_found = report.get(
        "skills_found",
        []
    )

    for name in skills_found:

        if not name:
            continue

        name = str(
            name
        ).strip()

        if not name:
            continue

        skill = Skill.objects.filter(
            name__iexact=name
        ).first()

        if skill:
            SeekerSkill.objects.get_or_create(
                seeker=profile,
                skill=skill,
                defaults={
                    "source": "resume"
                },
            )


class ResumeListCreateView(APIView):

    permission_classes = [IsSeeker]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    # =========================================================
    # GET /api/resumes/
    # =========================================================

    def get(self, request):

        resumes = (
            request.user
            .seeker_profile
            .resumes
            .all()[:20]
        )

        return Response(
            [
                resume_payload(
                    resume,
                    request
                )
                for resume in resumes
            ]
        )

    # =========================================================
    # POST /api/resumes/
    # =========================================================

    def post(self, request):

        profile = request.user.seeker_profile

        # -----------------------------------------------------
        # 1. Get uploaded file
        # -----------------------------------------------------

        upload = request.FILES.get(
            "file"
        )

        if upload is None:
            raise ValidationError(
                {
                    "detail": (
                        "Please choose a resume file."
                    )
                }
            )

        # -----------------------------------------------------
        # 2. Check extension
        # -----------------------------------------------------

        ext = (
            os.path.splitext(
                upload.name
            )[1]
            .lower()
            .lstrip(".")
        )

        if ext not in SIGNATURES:
            raise ValidationError(
                {
                    "detail": (
                        "Only PDF or DOCX files "
                        "are accepted."
                    )
                }
            )

        # -----------------------------------------------------
        # 3. Check file size
        # -----------------------------------------------------

        if (
            upload.size
            > settings.MAX_RESUME_MB * 1024 * 1024
        ):
            raise ValidationError(
                {
                    "detail": (
                        "File is too large. "
                        "Maximum size is %d MB."
                        % settings.MAX_RESUME_MB
                    )
                }
            )

        # -----------------------------------------------------
        # 4. Read file
        # -----------------------------------------------------

        data = upload.read()

        upload.seek(0)

        # -----------------------------------------------------
        # 5. Check file signature
        # -----------------------------------------------------

        if not data.startswith(
            SIGNATURES[ext]
        ):
            raise ValidationError(
                {
                    "detail": (
                        "This file does not look "
                        "like a valid %s."
                        % ext.upper()
                    )
                }
            )

        # -----------------------------------------------------
        # 6. Extract text
        # -----------------------------------------------------

        try:

            parsed = extract_text(
                io.BytesIO(data),
                ext,
            )

        except Exception as exc:

            logger.exception(
                "Resume parsing failed for %s",
                upload.name,
            )

            raise ValidationError(
                {
                    "detail": (
                        "We could not read this file "
                        "(%s). Export it again as a "
                        "text-based PDF or DOCX."
                        % type(exc).__name__
                    )
                }
            )

        # -----------------------------------------------------
        # 7. Safety check
        # -----------------------------------------------------

        if not isinstance(
            parsed,
            dict
        ):
            logger.error(
                "extract_text() returned unexpected type: %s",
                type(parsed).__name__,
            )

            raise ValidationError(
                {
                    "detail": (
                        "Resume parser returned "
                        "an invalid result."
                    )
                }
            )

        parsed_text = (
            parsed.get(
                "text",
                ""
            )
            or ""
        )

        # -----------------------------------------------------
        # 8. ATS scan
        #
        # IMPORTANT:
        # scan() expects the COMPLETE parsed dictionary,
        # NOT parsed["text"].
        # -----------------------------------------------------

        report = scan(
            parsed,
            list(
                Skill.objects.values_list(
                    "name",
                    flat=True,
                )
            ),
        )

        # -----------------------------------------------------
        # 9. Extract profile information
        # -----------------------------------------------------

        info = extract_profile(
            parsed_text
        )

        logger.info(
            "Extracted resume profile information: %s",
            info,
        )

        # -----------------------------------------------------
        # 10. Check ATS pass/fail
        # -----------------------------------------------------

        passed = (
            report.get(
                "score",
                0
            )
            >= settings.ATS_PASS_SCORE
        )

        # -----------------------------------------------------
        # 11. Save resume
        # -----------------------------------------------------

        with transaction.atomic():

            resume = Resume.objects.create(

                seeker=profile,

                file=upload,

                original_name=upload.name[:255],

                parsed_text=parsed_text[:60000],

                projects_text=info.get(
                    "projects_text",
                    ""
                )[:20000],

                ats_score=report.get(
                    "score",
                    0
                ),

                ats_report=report,

                passed=passed,

                is_active=False,
            )

            # -------------------------------------------------
            # 12. Only passed resumes become active
            # -------------------------------------------------

            if passed:

                activate_resume(
                    profile,
                    resume,
                    report,
                    info,
                )

        # -----------------------------------------------------
        # 13. Return response
        # -----------------------------------------------------

        return Response(
            resume_payload(
                resume,
                request
            ),
            status=201,
        )


# =============================================================
# PROFILE
# =============================================================


def profile_payload(profile):

    return {

        "full_name": profile.full_name,

        "email": profile.user.email,

        "phone": profile.phone,

        "location": profile.location,

        "education": profile.education,

        "grad_year": profile.grad_year,

        "experience_level": profile.experience_level,

        "open_to_relocate": profile.open_to_relocate,

        "ats_score": profile.ats_score,

        "skills": sorted(
            SeekerSkill.objects
            .filter(
                seeker=profile
            )
            .values_list(
                "skill__name",
                flat=True,
            )
        ),

        "has_active_resume": (
            profile.resumes
            .filter(
                is_active=True
            )
            .exists()
        ),

        "campus": (
            profile.campus.name
            if profile.campus
            else None
        ),
    }


class SeekerProfileView(APIView):

    permission_classes = [IsSeeker]

    parser_classes = [
        JSONParser
    ]

    # =========================================================
    # GET PROFILE
    # =========================================================

    def get(self, request):

        return Response(
            profile_payload(
                request.user.seeker_profile
            )
        )

    # =========================================================
    # UPDATE PROFILE
    # =========================================================

    def patch(self, request):

        profile = request.user.seeker_profile

        data = request.data

        # -----------------------------------------------------
        # 1. Basic text fields
        # -----------------------------------------------------

        limits = {

            "full_name": 150,

            "phone": 30,

            "location": 120,

            "education": 200,
        }

        for field, limit in limits.items():

            if field in data:

                setattr(
                    profile,
                    field,
                    str(
                        data[field] or ""
                    ).strip()[:limit],
                )

        # -----------------------------------------------------
        # 2. Keep User full name synchronized
        # -----------------------------------------------------

        if (
            "full_name" in data
            and profile.full_name
        ):

            request.user.full_name = (
                profile.full_name
            )

            request.user.save(
                update_fields=[
                    "full_name"
                ]
            )

        # -----------------------------------------------------
        # 3. Graduation year
        # -----------------------------------------------------

        if "grad_year" in data:

            value = data[
                "grad_year"
            ]

            if value in (
                "",
                None,
            ):

                profile.grad_year = None

            else:

                try:

                    year = int(
                        value
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    raise ValidationError(
                        {
                            "grad_year": (
                                "Enter a valid year."
                            )
                        }
                    )

                if not (
                    1990 <= year <= 2040
                ):

                    raise ValidationError(
                        {
                            "grad_year": (
                                "Enter a year between "
                                "1990 and 2040."
                            )
                        }
                    )

                profile.grad_year = year

        # -----------------------------------------------------
        # 4. Experience level
        # -----------------------------------------------------

        if "experience_level" in data:

            valid_levels = dict(
                SeekerProfile.EXP_LEVELS
            )

            if (
                data["experience_level"]
                not in valid_levels
            ):

                raise ValidationError(
                    {
                        "experience_level": (
                            "Invalid experience level."
                        )
                    }
                )

            profile.experience_level = (
                data["experience_level"]
            )

        # -----------------------------------------------------
        # 5. Relocation
        # -----------------------------------------------------

        if "open_to_relocate" in data:

            value = data[
                "open_to_relocate"
            ]

            if isinstance(
                value,
                str
            ):

                profile.open_to_relocate = (
                    value.lower()
                    in [
                        "true",
                        "1",
                        "yes",
                        "on",
                    ]
                )

            else:

                profile.open_to_relocate = bool(
                    value
                )

        # -----------------------------------------------------
        # 6. Save profile
        # -----------------------------------------------------

        profile.save()

        # -----------------------------------------------------
        # 7. Skills
        # -----------------------------------------------------

        ignored = []

        if (
            "skills" in data
            and isinstance(
                data["skills"],
                list,
            )
        ):

            SeekerSkill.objects.filter(
                seeker=profile
            ).delete()

            for raw in data[
                "skills"
            ][:60]:

                name = str(
                    raw
                ).strip()

                if not name:
                    continue

                skill = Skill.objects.filter(
                    name__iexact=name
                ).first()

                if skill:

                    SeekerSkill.objects.get_or_create(
                        seeker=profile,
                        skill=skill,
                        defaults={
                            "source": "manual"
                        },
                    )

                else:

                    ignored.append(
                        name
                    )

        # -----------------------------------------------------
        # 8. Return updated profile
        # -----------------------------------------------------

        payload = profile_payload(
            profile
        )

        payload[
            "ignored_skills"
        ] = ignored

        return Response(
            payload
        )