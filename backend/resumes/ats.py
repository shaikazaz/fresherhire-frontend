"""Rule-based ATS resume scanner. Pure Python (no Django) so it is easy to test.

Score out of 100:
  Contact details 15 | Standard sections 25 | Readable format 20
  Skill keywords 20  | Action verbs and results 10 | Length 10
"""
import math
import re

HEADINGS = {
    "education": ["education", "academic background", "academics", "qualification", "qualifications",
                  "educational qualification", "educational qualifications", "education and qualifications"],
    "skills": ["skills", "technical skills", "key skills", "core skills", "skills and tools", "technologies",
               "tech stack", "core competencies", "technical proficiency"],
    "projects": ["projects", "academic projects", "personal projects", "project experience", "key projects",
                 "projects and achievements", "major projects"],
    "experience": ["experience", "work experience", "professional experience", "internship", "internships",
                   "internship experience", "employment history", "work history", "training and internships"],
}
OTHER_HEADINGS = ["summary", "professional summary", "objective", "career objective", "profile", "certifications",
                  "certification", "achievements", "awards", "languages", "interests", "hobbies", "declaration",
                  "references", "extracurricular", "extracurricular activities", "courses", "training"]

_LOOKUP = {}
for _key, _names in HEADINGS.items():
    for _n in _names:
        _LOOKUP[_n] = _key
for _n in OTHER_HEADINGS:
    _LOOKUP[_n] = "other"

ACTION_VERBS = [
    "developed", "built", "designed", "implemented", "created", "led", "managed", "improved", "optimized",
    "automated", "analyzed", "deployed", "integrated", "launched", "delivered", "reduced", "increased",
    "engineered", "architected", "collaborated", "coordinated", "organized", "achieved", "established",
    "migrated", "tested", "debugged", "maintained", "configured", "trained", "mentored", "resolved",
    "streamlined", "researched", "presented", "wrote", "contributed", "programmed", "constructed",
]

SKILL_ALIASES = {
    "reactjs": "React", "react.js": "React", "nodejs": "Node.js", "node js": "Node.js",
    "postgres": "PostgreSQL", "mongo": "MongoDB", "js": "JavaScript", "ml": "Machine Learning",
    "tailwind": "Tailwind CSS", "restful": "REST API", "rest apis": "REST API", "scikit learn": "Scikit-learn",
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_CANDIDATE_RE = re.compile(r"\+?\d[\d\s\-().]{8,16}\d")
LINK_RE = re.compile(r"linkedin\.com|github\.com|gitlab\.com|portfolio", re.I)
METRIC_RE = re.compile(
    r"\d+(?:\.\d+)?\s?%|\d+(?:\.\d+)?\s?(?:\+|x\b|k\b|users|students|records|requests|projects|apps|"
    r"applications|hours|ms|customers|employees|members|participants|teams|features|endpoints|apis|"
    r"tests|models)",
    re.I,
)


def _norm_heading(line):
    line = line.lower().replace("&", " and ")
    line = re.sub(r"[^a-z ]", " ", line)
    return " ".join(line.split())


def split_sections(text):
    """Split resume text into {'header','education','skills','projects','experience','other'}."""
    sections = {"header": []}
    current = "header"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        key = _LOOKUP.get(_norm_heading(line)) if len(line) <= 45 else None
        if key:
            current = key
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def find_phone(text):
    for m in PHONE_CANDIDATE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 10 <= len(digits) <= 13:
            return m.group(0).strip()
    return None


def find_skills(text, skill_names):
    """Return canonical skill names (from the master list) found in the text."""
    low = text.lower()
    master = {s.lower(): s for s in skill_names}
    found = set()

    def present(term):
        return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", low) is not None

    for lower_name, canonical in master.items():
        if present(lower_name):
            found.add(canonical)
    for alias, target in SKILL_ALIASES.items():
        if target.lower() in master and present(alias):
            found.add(master[target.lower()])
    return sorted(found)


def _check(label, points, maximum, tip):
    return {"label": label, "points": points, "max": maximum, "passed": points >= maximum, "tip": tip}


def _group(key, label, checks):
    return {
        "key": key,
        "label": label,
        "points": sum(c["points"] for c in checks),
        "max": sum(c["max"] for c in checks),
        "checks": checks,
    }


def scan(parsed, skill_names):
    """parsed = {'text','pages','tables','images'}. Returns the full ATS report."""
    text = parsed.get("text", "") or ""
    low = text.lower()
    sections = split_sections(text)
    words = re.findall(r"[A-Za-z0-9+#.]+", text)
    word_count = len(words)
    pages = parsed.get("pages") or max(1, math.ceil(word_count / 450))

    # 1. Contact details (15)
    has_email = bool(EMAIL_RE.search(text))
    has_phone = find_phone(text) is not None
    has_link = bool(LINK_RE.search(text))
    contact = _group("contact", "Contact details", [
        _check("Email address", 5 if has_email else 0, 5, "Add a professional email address at the top"),
        _check("Phone number", 5 if has_phone else 0, 5, "Add your phone number at the top"),
        _check("LinkedIn / GitHub link", 5 if has_link else 0, 5, "Add your LinkedIn or GitHub profile link"),
    ])

    # 2. Standard sections (25)
    def has(key):
        return bool(sections.get(key, "").strip())

    section_group = _group("sections", "Standard sections", [
        _check("Education section", 7 if has("education") else 0, 7, "Add an Education section with a clear heading"),
        _check("Skills section", 7 if has("skills") else 0, 7, "Add a Skills section listing your tools and technologies"),
        _check("Projects section", 6 if has("projects") else 0, 6, "Add a Projects section (freshers are judged on projects)"),
        _check("Experience / Internship section", 5 if has("experience") else 0, 5,
               "Add an Experience or Internships section (training and volunteering also count)"),
    ])

    # 3. Readable format (20)
    n_chars = len(text.strip())
    text_pts = 10 if n_chars >= 200 else (5 if n_chars >= 80 else 0)
    fmt = _group("format", "Readable format", [
        _check("Text can be read by machines", text_pts, 10,
               "Export your resume as a text-based PDF or DOCX (not a scanned image)"),
        _check("No tables or columns", 5 if not parsed.get("tables") else 0, 5,
               "Remove tables and multi-column layouts; use a single-column format"),
        _check("No images or graphics", 5 if not parsed.get("images") else 0, 5,
               "Remove photos, logos and graphics; ATS systems cannot read them"),
    ])

    # 4. Skill keywords (20)
    skills_found = find_skills(text, skill_names)
    skill_pts = min(20, len(skills_found) * 2)
    skills_group = _group("skills", "Skill keywords", [
        _check("Relevant skill keywords (10+ for full marks)", skill_pts, 20,
               "Add more relevant skills; found %d, aim for 10 or more" % len(skills_found)),
    ])

    # 5. Action verbs and results (10)
    verbs_found = {v for v in ACTION_VERBS if re.search(r"\b" + v + r"\b", low)}
    verb_pts = 5 if len(verbs_found) >= 6 else 3 if len(verbs_found) >= 3 else 1 if verbs_found else 0
    metrics = METRIC_RE.findall(text)
    metric_pts = 5 if len(metrics) >= 2 else 3 if len(metrics) == 1 else 0
    impact = _group("impact", "Action verbs and results", [
        _check("Action verbs in bullet points", verb_pts, 5,
               "Start bullets with action verbs such as Built, Designed, Improved (found %d)" % len(verbs_found)),
        _check("Measurable results", metric_pts, 5,
               "Add numbers to your bullets, for example 'reduced load time by 30%'"),
    ])

    # 6. Length (10)
    if 150 <= word_count <= 700:
        word_pts = 5
    elif 100 <= word_count < 150 or 700 < word_count <= 900:
        word_pts = 3
    else:
        word_pts = 0
    page_pts = 5 if pages <= 1 else 3 if pages == 2 else 0
    length = _group("length", "Length", [
        _check("Word count (150 to 700 words)", word_pts, 5,
               "Aim for 150 to 700 words; yours has %d" % word_count),
        _check("One page for freshers", page_pts, 5, "Keep the resume to one page (two at most)"),
    ])

    groups = [contact, section_group, fmt, skills_group, impact, length]
    score = sum(g["points"] for g in groups)
    fixes = []
    for g in groups:
        for c in g["checks"]:
            if c["points"] < c["max"]:
                fixes.append("%s (+%d points)" % (c["tip"], c["max"] - c["points"]))
    return {
        "score": int(score),
        "groups": groups,
        "fixes": fixes,
        "skills_found": skills_found,
        "sections_found": [k for k in ("education", "skills", "projects", "experience") if has(k)],
        "word_count": word_count,
        "pages": pages,
    }
