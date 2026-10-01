from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial=True
    dependencies=[("jobs","0001_initial")]
    operations=[migrations.CreateModel(name="SkillResource",fields=[
        ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
        ("kind",models.CharField(choices=[("course","Course"),("project","Project idea")],default="course",max_length=10)),
        ("title",models.CharField(max_length=200)),
        ("url",models.URLField(blank=True)),
        ("provider",models.CharField(blank=True,max_length=100)),
        ("skill",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="resources",to="jobs.skill")),
    ])]
