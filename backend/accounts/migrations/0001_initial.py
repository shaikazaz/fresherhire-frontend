from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion
import django.contrib.auth.models
import accounts.models
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]
    operations = [
        migrations.CreateModel(
            name="Campus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("invite_code", models.CharField(max_length=50, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"verbose_name_plural": "campuses"},
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("full_name", models.CharField(blank=True, max_length=150)),
                ("role", models.CharField(choices=[("seeker","Job seeker"),("recruiter","Recruiter"),("admin","Admin")], default="seeker", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_verified", models.BooleanField(default=False)),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now)),
                ("groups", models.ManyToManyField(blank=True, related_name="custom_user_set", related_query_name="user", to="auth.group")),
                ("user_permissions", models.ManyToManyField(blank=True, related_name="custom_user_set", related_query_name="user", to="auth.permission")),
            ],
            options={"swappable": "AUTH_USER_MODEL"},
            managers=[("objects", accounts.models.UserManager())],
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("website", models.URLField(blank=True)),
                ("industry", models.CharField(blank=True, max_length=100)),
                ("size", models.CharField(blank=True, max_length=50)),
                ("description", models.TextField(blank=True)),
                ("is_verified", models.BooleanField(default=False)),
                ("is_claimed", models.BooleanField(default=True)),
                ("source", models.CharField(choices=[("self_signup","Self signup"),("seeded","Seeded by admin"),("campus","Campus")], default="self_signup", max_length=20)),
                ("response_rate", models.FloatField(default=0)),
                ("avg_response_hours", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("recruiter_user", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="company", to="accounts.user")),
            ],
            options={"verbose_name_plural": "companies"},
        ),
        migrations.CreateModel(
            name="SeekerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(blank=True, max_length=150)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("education", models.CharField(blank=True, max_length=200)),
                ("grad_year", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("experience_level", models.CharField(choices=[("fresher","Fresher"),("junior","0-2 years"),("mid","2-5 years")], default="fresher", max_length=20)),
                ("open_to_relocate", models.BooleanField(default=False)),
                ("ats_score", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("campus", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="seekers", to="accounts.campus")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="seeker_profile", to="accounts.user")),
            ],
        ),
    ]
