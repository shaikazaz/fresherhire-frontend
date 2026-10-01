# FresherHire: Day 1 build (Django + MySQL + React)

A fresher-first job marketplace. Day 1 covers: setup, JWT login with roles, all database tables, jobs with
filters, resume upload with ATS score, match score, one-click apply, seeker counters and the career guide.

```
jobportal/
  backend/    Django + Django REST Framework + MySQL
  frontend/   React (Vite) + Tailwind CSS
```

## Order to do things (follow this exactly)

Do one step at a time. Do not move on until the step works.

| # | Step | You should see |
|---|------|----------------|
| 1 | Install Python 3.10-3.12, Node.js 18+, MySQL 8, VS Code | `python --version`, `node -v`, MySQL running |
| 2 | Create the MySQL database (below) | No error |
| 3 | Backend: virtual env, `pip install`, `.env` | Packages install |
| 4 | Run the pure tests (below) | `OK`, 11 tests |
| 5 | `makemigrations`, `migrate` | Tables created in MySQL |
| 6 | `seed_demo`, `runserver` | http://127.0.0.1:8000/api/health/ shows `{"status": "ok"}` |
| 7 | Run the Django tests | `OK` |
| 8 | Frontend: `npm install`, `npm run dev` | http://localhost:5173 opens |
| 9 | Walk through the demo checklist (bottom) | Each item works |

## 1. MySQL

```sql
CREATE DATABASE jobportal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2. Backend (terminal 1)

Windows (PowerShell):
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Mac / Linux:
```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `backend/.env` and set `DB_PASSWORD` (and `DB_USER` if it is not `root`).
For a quick test without MySQL set `DB_ENGINE=sqlite`. For the assessment use `mysql`.

Test the scoring logic first (needs no database):
```
python -m unittest discover -s tests_pure -v
```

Create tables and load demo data:
```
python manage.py makemigrations accounts jobs resumes applications careers notifications billing crm
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Run the API tests (in another terminal with the venv active):
```
python manage.py test
```

## 3. Frontend (terminal 2)

```
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. Vite forwards `/api` and `/media` to Django on port 8000, so no CORS setup is needed.

## Demo accounts (created by `seed_demo`)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@demo.com | Admin@12345 |
| Recruiter | recruiter@demo.com | Recruiter@123 |
| Seeker | seeker@demo.com | Seeker@123 |

Django admin: http://127.0.0.1:8000/admin/ (log in as admin@demo.com).
Sample resumes to upload: `backend/sample_data/sample_resume.pdf` (scores 100), `sample_resume.docx`,
and `weak_resume.pdf` (scores 20, shows the fix list).
Campus join link: http://localhost:5173/join/jntu-hyd

## Day 1 demo checklist

1. Home page loads with latest jobs.
2. Log in as **seeker@demo.com**, go to Resume & ATS, upload `weak_resume.pdf`. It scores low and shows fixes.
3. Upload `sample_resume.pdf`. It passes, becomes your active resume and fills your profile and skills.
4. Open Jobs. Jobs are now ranked with match scores. Try each filter (location, skills, job type, experience, salary, posted).
5. Open a job. You see the match breakdown, matched and missing skills and slots left.
6. Click Apply. Dashboard counters (Eligible, Applied, Placed) update.
7. Open Career guide. You see missing skills ranked by demand, courses and project ideas.
8. Log in as **recruiter@demo.com**, post a job, see it on the dashboard and in the job list.
9. Log in as **admin@demo.com**, see platform stats.

## Settings you may want to change (`backend/.env`)

- `ATS_PASS_SCORE` (default 75): the minimum ATS score for a resume to become active.
- `MAX_RESUME_MB` (default 5).

## Troubleshooting

- `mysqlclient` errors on Windows: not needed. This project uses PyMySQL automatically.
- `Access denied for user`: fix `DB_USER` and `DB_PASSWORD` in `.env`.
- `Unknown database 'jobportal'`: run the `CREATE DATABASE` statement.
- Login works but pages show "Cannot reach the server": the backend is not running on port 8000.
- `Table ... doesn't exist`: run `makemigrations` (with the app names) and `migrate` again.
- A migration error after editing models in development: drop and recreate the database, delete the
  `migrations/00*.py` files in each app, and run the commands again.

## What is in Day 1 and what comes on Day 2

Done (Day 1): project setup, roles and JWT login, models for all tables, admin, React shell with protected
routes, jobs API with 6+ filters and slug URLs, job posting, resume upload and ATS score, profile from resume,
match score, one-click apply with first-come cap and waitlist, seeker counters, career guide.

Day 2: applicant ranking for recruiters, shortlist/reject with feedback, extend cap and best-match window,
interviews, candidate search, plans, notifications, SLA command, HubSpot sync, admin analytics, Razorpay test.
Their tables already exist.

## Day 2 additions included

- Ranked recruiter applicants
- Shortlist/reject with feedback reason
- Application-cap extension and waitlist promotion
- Best-match-window finalization
- Interview scheduling, completion, seeker confirmation and contact unlock
- Candidate search with 7 filters
- Recruiter plans and job-limit enforcement
- In-app matching-job notifications
- Configurable email notifications for matching jobs


## Added completion work
- Registered the seeker dashboard API route.
- Added recruiter rejection-reason validation.
- Added response SLA status to application payloads.
- Added `python manage.py sla_feedback` for automatic SLA feedback.
- Added HubSpot signup sync with `crm_sync_log` (configure `HUBSPOT_ACCESS_TOKEN`).
- Added admin marketplace analytics API and React dashboard.
- Added seeker interview confirmation and recruiter interview completion UI.
- Added recruiter cap extension and best-match promotion controls.
- Added best-match jobs a 24-hour review window on creation.
