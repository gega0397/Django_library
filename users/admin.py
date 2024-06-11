from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.forms import CustomUserCreationFormAdmin, CustomUserChangeFormAdmin
from users.models import CustomUser



@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    search_fields = ['email', 'first_name', 'last_name', 'personal_number']
    add_form = CustomUserCreationFormAdmin
    form = CustomUserChangeFormAdmin
    model = CustomUser
    list_display = ["email", 'user_type', 'first_name', 'last_name', 'personal_number', 'birth_date', 'is_authorized']
    ordering = ['date_joined']
    list_filter = ['is_authorized', 'user_type']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'personal_number', 'birth_date',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_authorized', 'user_type',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name',
                'last_name', 'password1', 'password2', 'personal_number', 'birth_date',
                'is_authorized', 'user_type',),
        }),
    )
