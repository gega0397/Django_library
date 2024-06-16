from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser
from django.conf import settings
from django.utils import timezone
from users.choices import UserTypeChoices
from django.db.models import Q


class Author(models.Model):
    name = models.CharField(max_length=20, verbose_name=_('Name'))
    surname = models.CharField(max_length=25, verbose_name=_('Surname'), blank=True, null=True)
    birth_date = models.DateField(verbose_name=_('Birth Date'), blank=True, null=True)

    def __str__(self):
        return self.name + ' ' + self.surname if self.surname else self.name

    class Meta:
        ordering = ['name']


class Genre(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Book(models.Model):
    authors = models.ManyToManyField(Author, related_name='books', verbose_name=_('Authors'))
    genres = models.ManyToManyField(Genre, related_name='books', verbose_name=_('Genres'))
    title = models.CharField(max_length=50, verbose_name=_('Title'))
    release_date = models.DateField(verbose_name=_('Release Date'), blank=True, null=True)
    stock = models.PositiveIntegerField(verbose_name=_('Stock'), default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['id']


class Borrow(models.Model):
    user = models.ForeignKey(CustomUser, related_name="borrows",
                             limit_choices_to=Q(user_type=UserTypeChoices.STUDENT) | Q(user_type=UserTypeChoices.SYSTEMS),
                             on_delete=models.CASCADE,
                             verbose_name=_('User'))
    book = models.ForeignKey(Book,
                             related_name="borrows",
                             on_delete=models.CASCADE,
                             verbose_name=_('Book'))
    borrowed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Borrowed At'))
    due_date = models.DateTimeField(verbose_name=_('Due Date'), default=timezone.now() + settings.BORROW_TIME_LIMIT)
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Returned At'))
    returned = models.BooleanField(default=False, verbose_name=_('Returned'))

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.due_date = timezone.now() + settings.BORROW_TIME_LIMIT
        if self.returned and not self.returned_at:
            self.returned_at = timezone.now()
        super().save(*args, **kwargs)


class Reserve(models.Model):
    user = models.ForeignKey(CustomUser, related_name="reserves",
                             limit_choices_to=Q(user_type=UserTypeChoices.STUDENT) | Q(user_type=UserTypeChoices.SYSTEMS),
                             on_delete=models.CASCADE,
                             verbose_name=_('User'))
    book = models.ForeignKey(Book,
                             related_name="reserves",
                             on_delete=models.CASCADE,
                             verbose_name=_('Book'))
    borrowed_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Borrowed At'))
    due_date = models.DateTimeField(verbose_name=_('Due Date'))
    status = models.BooleanField(default=True, verbose_name=_('Status'))

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.due_date = timezone.now() + settings.RESERVE_TIME_LIMIT
        if not self.status:
            self.due_date = timezone.now()
        super().save(*args, **kwargs)
