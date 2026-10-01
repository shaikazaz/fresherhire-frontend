from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", "admin")
        return self._create_user(email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    ROLES = [("seeker", "Job seeker"), ("recruiter", "Recruiter"), ("admin", "Admin")]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLES, default="seeker")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Campus(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True)
    invite_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "campuses"

    def __str__(self):
        return self.name


class SeekerProfile(models.Model):
    EXP_LEVELS = [("fresher", "Fresher"), ("junior", "0-2 years"), ("mid", "2-5 years")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seeker_profile")
    campus = models.ForeignKey(Campus, null=True, blank=True, on_delete=models.SET_NULL, related_name="seekers")
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=120, blank=True)
    education = models.CharField(max_length=200, blank=True)
    grad_year = models.PositiveSmallIntegerField(null=True, blank=True)
    experience_level = models.CharField(max_length=20, choices=EXP_LEVELS, default="fresher")
    open_to_relocate = models.BooleanField(default=False)
    ats_score = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or self.user.email


class Company(models.Model):
    SOURCES = [("self_signup", "Self signup"), ("seeded", "Seeded by admin"), ("campus", "Campus")]

    recruiter_user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="company"
    )
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_claimed = models.BooleanField(default=True)
    source = models.CharField(max_length=20, choices=SOURCES, default="self_signup")
    response_rate = models.FloatField(default=0)
    avg_response_hours = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name
