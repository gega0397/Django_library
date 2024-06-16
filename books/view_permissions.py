from rest_framework import permissions
from users.models import UserTypeChoices
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class CreatePermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_user_types = [
            UserTypeChoices.ADMIN.value,
            UserTypeChoices.LIBRARIAN.value,
            UserTypeChoices.SYSTEMS.value
        ]

        return int(request.user.user_type) in allowed_user_types
2

class CreateUpdateReserveBorrow(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            user_type = request.user.user_type
            if user_type == UserTypeChoices.STUDENT:
                user_id = request.data.get('user')
                return str(request.user.id) == user_id
            elif user_type in [UserTypeChoices.LIBRARIAN, UserTypeChoices.ADMIN, UserTypeChoices.SYSTEMS]:
                return True
        return False



class IsSystemUser(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # print(request.user.user_type)
        # print(UserTypeChoices.SYSTEMS)
        return int(request.user.user_type) == int(UserTypeChoices.SYSTEMS)