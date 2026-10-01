from rest_framework.permissions import BasePermission


class _RolePermission(BasePermission):
    role = None

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == self.role)


class IsSeeker(_RolePermission):
    role = "seeker"


class IsRecruiter(_RolePermission):
    role = "recruiter"


class IsPlatformAdmin(_RolePermission):
    role = "admin"
