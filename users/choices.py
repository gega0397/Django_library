from django.db import models


class UserTypeChoices(models.IntegerChoices):
    STUDENT = 1, "client"
    LIBRARIAN = 2, "librarian"
    ADMIN = 3, "admin"
    SYSTEMS = 4, "systems"


class UserTypeChoicesForm(models.IntegerChoices):
    STUDENT = 1, "client"
