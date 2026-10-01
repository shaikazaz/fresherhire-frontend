from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm as BaseUserChangeForm

from .models import Campus, Company, SeekerProfile, User


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("email", "full_name", "role")


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    ordering = ("email",)
    list_display = ("email", "full_name", "role", "is_active", "is_verified", "date_joined")
    list_filter = ("role", "is_active", "is_verified")
    search_fields = ("email", "full_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("full_name", "role", "is_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "full_name", "role", "password1", "password2")}),
    )


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "invite_code", "created_at")
    search_fields = ("name", "invite_code")


@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "location", "grad_year", "ats_score", "campus")
    search_fields = ("full_name", "user__email")
    list_filter = ("experience_level", "campus")


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "is_verified", "is_claimed", "source", "created_at")
    list_filter = ("is_verified", "is_claimed", "source")
    search_fields = ("name",)
    actions = ["verify_companies"]

    @admin.action(description="Mark selected companies as verified")
    def verify_companies(self, request, queryset):
        queryset.update(is_verified=True)
