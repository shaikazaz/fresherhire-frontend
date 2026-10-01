import os,sys,unittest
sys.path.insert(0,os.path.join(os.path.dirname(__file__),".."))
from applications.match import compute_match
from resumes.ats import scan
class Day3ScoreTests(unittest.TestCase):
    def test_ats_score_is_bounded(self):
        r=scan({"text":"Python Django SQL","pages":1,"tables":0,"images":0},["Python","Django","SQL"]); self.assertGreaterEqual(r["score"],0); self.assertLessEqual(r["score"],100)
    def test_match_score_is_bounded_and_additive(self):
        seeker={"skills":{"python","django"},"projects_text":"Django REST API project","ats":90,"education":"B.Tech","grad_year":2025,"location":"Hyderabad","open_to_relocate":False}
        job={"title":"Python Developer","description":"Build Django REST APIs","location":"Hyderabad","skills":[("Python",True),("Django",True)]}
        r=compute_match(seeker,job,today_year=2026); self.assertGreaterEqual(r["score"],0); self.assertLessEqual(r["score"],100); self.assertEqual(r["score"],round(sum(x["points"] for x in r["breakdown"])))
