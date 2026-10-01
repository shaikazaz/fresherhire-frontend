# FresherHire — Day 1 + Day 2 + Day 3

This folder merges the working Day 1/2 project with the Day 3 pending features.

## Day 3 additions
- Razorpay test-mode create-order, checkout, signature verification and plan activation
- SEO job list/detail pages
- JobPosting JSON-LD
- sitemap.xml and robots.txt
- 32 demo jobs in seed command
- Day 3 score tests
- Recruiter Plans UI with Razorpay checkout and loading/error/empty states

## Run
```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py seed_demo
python -m unittest discover -s tests_pure -v
```

Frontend:
```powershell
cd frontend
npm install
npm run build
```

## Razorpay
Put test credentials in `backend/.env`:
`RAZORPAY_KEY_ID=`
`RAZORPAY_KEY_SECRET=`
Never commit the secret.

## Day 3 SEO URLs
- `/seo/jobs/`
- `/seo/jobs/<slug>/`
- `/sitemap.xml`
- `/robots.txt`
