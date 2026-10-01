from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Campus, Company, SeekerProfile, User


class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role", "is_verified", "company_name"]

    def get_company_name(self, obj):
        company = getattr(obj, "company", None)
        return company.name if company else None


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    full_name = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=["seeker", "recruiter"])
    campus_code = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True, max_length=200)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_campus_code(self, value):
        value = value.strip()
        if value and not Campus.objects.filter(invite_code__iexact=value).exists():
            raise serializers.ValidationError("This campus code is not valid.")
        return value

    def validate(self, attrs):
        if attrs["role"] == "recruiter" and not attrs.get("company_name", "").strip():
            raise serializers.ValidationError({"company_name": "Company name is required for recruiters."})
        return attrs

    @transaction.atomic
    def create(self, data):
        user = User.objects.create_user(
            email=data["email"], password=data["password"], full_name=data["full_name"], role=data["role"]
        )
        if data["role"] == "seeker":
            code = data.get("campus_code", "")
            campus = Campus.objects.filter(invite_code__iexact=code).first() if code else None
            SeekerProfile.objects.create(user=user, full_name=data["full_name"], campus=campus)
        else:
            Company.objects.create(
                recruiter_user=user,
                name=data["company_name"].strip(),
                source="self_signup",
            )
        # CRM sync runs after the database transaction commits.
        from django.db import transaction
        from crm.services import sync_user_to_hubspot
        transaction.on_commit(lambda: sync_user_to_hubspot(user))
        return user
