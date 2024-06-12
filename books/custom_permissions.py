from rest_framework.permissions import BasePermission
from users.choices import UserTypeChoices


class IsSystemUser(BasePermission):

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # print(request.user.user_type)
        # print(UserTypeChoices.SYSTEMS)
        return int(request.user.user_type) == int(UserTypeChoices.SYSTEMS)
