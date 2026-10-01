from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial=True
    dependencies=[("accounts","0001_initial"),("jobs","0001_initial"),("resumes","0001_initial")]
    operations=[
        migrations.CreateModel(name="Application",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("match_score",models.PositiveSmallIntegerField(default=0)),
            ("status",models.CharField(choices=[("applied","Applied"),("waitlisted","Waitlisted"),("shortlisted","Shortlisted"),("interview_scheduled","Interview scheduled"),("interview_completed","Interview completed"),("feedback_given","Feedback given"),("offered","Offered"),("placed","Placed"),("rejected","Rejected"),("withdrawn","Withdrawn")],default="applied",max_length=25)),
            ("applied_at",models.DateTimeField(auto_now_add=True)),
            ("response_due_at",models.DateTimeField(blank=True,null=True)),
            ("responded_at",models.DateTimeField(blank=True,null=True)),
            ("job",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="applications",to="jobs.job")),
            ("resume",models.ForeignKey(null=True,on_delete=django.db.models.deletion.SET_NULL,related_name="applications",to="resumes.resume")),
            ("seeker",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="applications",to="accounts.seekerprofile")),
        ],options={"ordering":["-applied_at"],"unique_together":{("job","seeker")}}),
        migrations.CreateModel(name="Interview",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("scheduled_at",models.DateTimeField()),
            ("mode",models.CharField(default="online",max_length=30)),
            ("recruiter_marked_done",models.BooleanField(default=False)),
            ("seeker_confirmed",models.BooleanField(default=False)),
            ("application",models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name="interview",to="applications.application")),
        ]),
        migrations.CreateModel(name="Feedback",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("reason_code",models.CharField(blank=True,max_length=50)),
            ("comments",models.TextField(blank=True)),
            ("is_system_generated",models.BooleanField(default=False)),
            ("missing_skills_json",models.JSONField(blank=True,default=list)),
            ("created_at",models.DateTimeField(auto_now_add=True)),
            ("application",models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name="feedback",to="applications.application")),
        ]),
    ]
