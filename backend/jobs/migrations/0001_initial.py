from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Skill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
            ],
            options={"ordering":["name"]},
        ),
        migrations.CreateModel(
            name="Job",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=255, unique=True)),
                ("description", models.TextField()),
                ("location", models.CharField(max_length=120)),
                ("job_type", models.CharField(choices=[("full_time","Full-time"),("internship","Internship"),("part_time","Part-time"),("hiring_drive","Hiring drive")], default="full_time", max_length=20)),
                ("exp_level", models.CharField(choices=[("fresher","Fresher"),("junior","0-2 years"),("mid","2-5 years")], default="fresher", max_length=20)),
                ("salary_min", models.PositiveIntegerField(blank=True, null=True)),
                ("salary_max", models.PositiveIntegerField(blank=True, null=True)),
                ("application_cap", models.PositiveIntegerField(default=50)),
                ("cap_mode", models.CharField(choices=[("first_come","First come"),("best_match_window","Best match window")], default="first_come", max_length=20)),
                ("min_match_score", models.PositiveSmallIntegerField(default=40)),
                ("review_window_ends_at", models.DateTimeField(blank=True, null=True)),
                ("response_sla_days", models.PositiveSmallIntegerField(default=7)),
                ("extended_count", models.PositiveIntegerField(default=0)),
                ("status", models.CharField(choices=[("draft","Draft"),("pending","Pending approval"),("active","Active"),("closed","Closed")], default="active", max_length=20)),
                ("jd_score", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="jobs", to="accounts.company")),
            ],
            options={"ordering":["-created_at"],"indexes":[models.Index(fields=["status","created_at"], name="jobs_job_status_277b31_idx")]},
        ),
        migrations.CreateModel(
            name="JobSkill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_required", models.BooleanField(default=True)),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="job_skills", to="jobs.job")),
                ("skill", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="job_links", to="jobs.skill")),
            ],
            options={"unique_together":{("job","skill")}},
        ),
    ]
