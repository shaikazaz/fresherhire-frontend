from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial=True
    dependencies=[("accounts","0001_initial"),("jobs","0001_initial")]
    operations=[
        migrations.CreateModel(name="Resume",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("file",models.FileField(upload_to="resumes/%Y/%m/")),
            ("original_name",models.CharField(blank=True,max_length=255)),
            ("parsed_text",models.TextField(blank=True)),
            ("projects_text",models.TextField(blank=True)),
            ("ats_score",models.PositiveSmallIntegerField(default=0)),
            ("ats_report",models.JSONField(blank=True,default=dict)),
            ("passed",models.BooleanField(default=False)),
            ("is_active",models.BooleanField(default=False)),
            ("uploaded_at",models.DateTimeField(auto_now_add=True)),
            ("seeker",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="resumes",to="accounts.seekerprofile")),
        ],options={"ordering":["-uploaded_at"]}),
        migrations.CreateModel(name="SeekerSkill",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("source",models.CharField(choices=[("resume","From resume"),("manual","Added manually")],default="resume",max_length=10)),
            ("seeker",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="seeker_skills",to="accounts.seekerprofile")),
            ("skill",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="seeker_links",to="jobs.skill")),
        ],options={"unique_together":{("seeker","skill")}}),
        migrations.CreateModel(name="Project",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("title",models.CharField(max_length=200)),
            ("description",models.TextField(blank=True)),
            ("tech_stack",models.CharField(blank=True,max_length=300)),
            ("seeker",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="projects",to="accounts.seekerprofile")),
        ]),
    ]
