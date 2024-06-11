from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from users.managers import CustomUserManager
from users.choices import UserTypeChoices


# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    personal_number = models.CharField(max_length=11, verbose_name=_("Personal Number"), unique=True)
    birth_date = models.DateField(_("Birth Date"))
    user_type = models.IntegerField(choices=UserTypeChoices.choices, blank=True, null=True,
                                 verbose_name=_("User Type"), default='client')
    is_authorized = models.BooleanField(default=True if settings.DEBUG else False, verbose_name=_("Is Authorized"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['user_type', 'first_name', 'last_name', 'personal_number', 'birth_date']

    objects = CustomUserManager()

    def __str__(self):
        return " ".join([self.first_name, self.last_name])

    def is_librarian(self):
        return self.user_type == 'librarian'

    def is_client(self):
        return self.user_type == 'client'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
