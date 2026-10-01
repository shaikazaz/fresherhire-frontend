"""Match score between a seeker and a job. Pure Python (no Django) so it is easy to test.

Score out of 100:
  Skills 40 | Projects/experience relevance 25 | Education fit 15 | Resume ATS quality 10 | Location 10
"""
import datetime
import re

STOPWORDS = set("""
the and for with that this from will have has are you your our their they them who what when where which
into onto over under about across after before between through during also can may must should would could
job role work working team teams looking candidate candidates required requirements responsibilities
experience skills knowledge ability strong good excellent understanding using use used etc per not all any
new including such more than other well able join company we us
""".split())


def tokens(text):
    return {w for w in re.findall(r"[a-z][a-z0-9+#]{2,}", (text or "").lower()) if w not in STOPWORDS}


def compute_match(seeker, job, today_year=None):
    """seeker: {'skills': set(lowercase), 'projects_text', 'ats', 'education', 'grad_year',
                'location', 'open_to_relocate'}
    job: {'title','description','location','skills': [(name, is_required), ...]}"""
    today_year = today_year or datetime.date.today().year
    job_skills = job.get("skills", [])
    required = [n for n, req in job_skills if req] or [n for n, _ in job_skills]
    have = seeker.get("skills", set())

    matched = [n for n in required if n.lower() in have]
    missing = [n for n in required if n.lower() not in have]
    if required:
        skills_pts = round(len(matched) / len(required) * 40, 1)
        skills_detail = "%d of %d required skills matched" % (len(matched), len(required))
    else:
        skills_pts = 20
        skills_detail = "No required skills listed"

    job_kw = tokens(job.get("title", "") + " " + job.get("description", "") + " " + " ".join(n for n, _ in job_skills))
    seeker_kw = tokens(seeker.get("projects_text", ""))
    overlap = len(job_kw & seeker_kw)
    ratio = min(1.0, overlap / max(1, min(10, len(job_kw)))) if job_kw else 0
    proj_pts = round(ratio * 25, 1)
    proj_detail = "%d keywords shared with the job" % overlap

    edu, year = seeker.get("education") or "", seeker.get("grad_year")
    if edu and year and year <= today_year + 1:
        edu_pts, edu_detail = 15, "Education details complete"
    elif edu or year:
        edu_pts, edu_detail = 7, "Education partly complete (add degree and graduation year)"
    else:
        edu_pts, edu_detail = 0, "Add your education to your profile"

    ats_pts = round((seeker.get("ats") or 0) * 0.10, 1)

    job_loc = (job.get("location") or "").lower()
    seek_loc = (seeker.get("location") or "").lower().strip()
    if "remote" in job_loc or (seek_loc and (seek_loc in job_loc or job_loc in seek_loc)):
        loc_pts, loc_detail = 10, "Location matches"
    elif seeker.get("open_to_relocate"):
        loc_pts, loc_detail = 5, "Open to relocate"
    else:
        loc_pts, loc_detail = 0, "Different city (turn on 'open to relocate' in your profile)"

    total = skills_pts + proj_pts + edu_pts + ats_pts + loc_pts
    return {
        "score": max(0, min(100, int(round(total)))),
        "matched_skills": matched,
        "missing_skills": missing,
        "breakdown": [
            {"key": "skills", "label": "Skills match", "points": skills_pts, "max": 40, "detail": skills_detail},
            {"key": "projects", "label": "Project relevance", "points": proj_pts, "max": 25, "detail": proj_detail},
            {"key": "education", "label": "Education fit", "points": edu_pts, "max": 15, "detail": edu_detail},
            {"key": "ats", "label": "Resume quality", "points": ats_pts, "max": 10,
             "detail": "Based on your ATS score"},
            {"key": "location", "label": "Location", "points": loc_pts, "max": 10, "detail": loc_detail},
        ],
    }
