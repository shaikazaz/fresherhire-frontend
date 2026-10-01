# Migration repair

The merged package was missing the original Day 1/Day 2 initial migration files while retaining the Day 3 billing migration that depends on billing/0001_initial.py.

This package restores the migration chain:
- accounts/0001_initial.py
- billing/0001_initial.py
- billing/0002_subscription_razorpay_fields.py
- crm/0001_initial.py
- jobs/0001_initial.py
- notifications/0001_initial.py
- resumes/0001_initial.py
- applications/0001_initial.py
- careers/0001_initial.py

On Windows, from backend with the venv active:
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py test
