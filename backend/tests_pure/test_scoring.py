"""Tests for the ATS scanner and match score. No Django needed:
    cd backend && python -m unittest discover -s tests_pure -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from applications.match import compute_match  # noqa: E402
from resumes.ats import find_skills, scan, split_sections  # noqa: E402
from resumes.parser import extract_profile, extract_text  # noqa: E402

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "sample_data")
SKILLS = ["Python", "Django", "JavaScript", "React", "SQL", "MySQL", "HTML", "CSS", "Git", "REST API",
          "Bootstrap", "Docker", "Java", "Node.js", "C++", "AWS"]


def open_sample(name):
    return open(os.path.join(SAMPLES, name), "rb")


class AtsTests(unittest.TestCase):
    def test_good_pdf_scores_high(self):
        with open_sample("sample_resume.pdf") as f:
            parsed = extract_text(f, "pdf")
        report = scan(parsed, SKILLS)
        self.assertGreaterEqual(report["score"], 75, report["fixes"])
        self.assertLessEqual(report["score"], 100)
        self.assertIn("Python", report["skills_found"])

    def test_good_docx_scores_high(self):
        with open_sample("sample_resume.docx") as f:
            parsed = extract_text(f, "docx")
        self.assertGreaterEqual(scan(parsed, SKILLS)["score"], 75)

    def test_weak_resume_scores_low_with_fixes(self):
        with open_sample("weak_resume.pdf") as f:
            parsed = extract_text(f, "pdf")
        report = scan(parsed, SKILLS)
        self.assertLess(report["score"], 50)
        self.assertTrue(any("Projects" in fix for fix in report["fixes"]))

    def test_group_maximums_sum_to_100(self):
        report = scan({"text": "x", "pages": 1, "tables": 0, "images": 0}, SKILLS)
        self.assertEqual(sum(g["max"] for g in report["groups"]), 100)

    def test_tables_and_images_lose_points(self):
        with open_sample("sample_resume.pdf") as f:
            parsed = extract_text(f, "pdf")
        base = scan(parsed, SKILLS)["score"]
        parsed["tables"], parsed["images"] = 1, 1
        self.assertEqual(scan(parsed, SKILLS)["score"], base - 10)

    def test_section_split_and_skill_detection(self):
        sections = split_sections("Name\nSkills:\nPython, C++\nProjects\nBuilt a thing")
        self.assertIn("Python", sections["skills"])
        self.assertIn("Built", sections["projects"])
        self.assertEqual(find_skills("I know C++ and reactjs", ["C++", "React", "Java"]), ["C++", "React"])
        self.assertEqual(find_skills("javascript only", ["Java", "JavaScript"]), ["JavaScript"])

    def test_profile_extraction(self):
        with open_sample("sample_resume.pdf") as f:
            profile = extract_profile(extract_text(f, "pdf")["text"])
        self.assertEqual(profile["email"], "ananya.reddy@example.com")
        self.assertTrue(profile["phone"].replace(" ", "").endswith("9876543210"))
        self.assertEqual(profile["grad_year"], 2025)
        self.assertIn("B.Tech", profile["education"])
        self.assertIn("Job Portal", profile["projects_text"])


class MatchTests(unittest.TestCase):
    seeker = {"skills": {"python", "django", "sql"}, "projects_text": "Built a Django job portal with MySQL and REST API",
              "ats": 80, "education": "B.Tech CSE", "grad_year": 2025, "location": "Hyderabad",
              "open_to_relocate": False}
    job = {"title": "Python Developer", "description": "Build Django REST APIs with MySQL for a job portal",
           "location": "Hyderabad", "skills": [("Python", True), ("Django", True), ("SQL", True), ("Docker", True)]}

    def test_score_and_lists(self):
        m = compute_match(self.seeker, self.job, today_year=2026)
        self.assertEqual(m["matched_skills"], ["Python", "Django", "SQL"])
        self.assertEqual(m["missing_skills"], ["Docker"])
        self.assertEqual(m["breakdown"][0]["points"], 30.0)  # 3 of 4 x 40
        self.assertEqual(m["breakdown"][2]["points"], 15)
        self.assertEqual(m["breakdown"][3]["points"], 8.0)
        self.assertEqual(m["breakdown"][4]["points"], 10)
        self.assertTrue(0 <= m["score"] <= 100)

    def test_total_is_sum_of_parts(self):
        m = compute_match(self.seeker, self.job, today_year=2026)
        self.assertEqual(m["score"], round(sum(b["points"] for b in m["breakdown"])))

    def test_location_and_relocation(self):
        far = dict(self.job, location="Pune")
        self.assertEqual(compute_match(self.seeker, far, 2026)["breakdown"][4]["points"], 0)
        reloc = dict(self.seeker, open_to_relocate=True)
        self.assertEqual(compute_match(reloc, far, 2026)["breakdown"][4]["points"], 5)
        remote = dict(self.job, location="Remote")
        self.assertEqual(compute_match(self.seeker, remote, 2026)["breakdown"][4]["points"], 10)

    def test_no_skills_listed_does_not_crash(self):
        job = dict(self.job, skills=[])
        self.assertTrue(0 <= compute_match(self.seeker, job, 2026)["score"] <= 100)


if __name__ == "__main__":
    unittest.main()
