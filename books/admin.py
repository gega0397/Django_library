from django.contrib import admin

from .forms import BorrowAdminForm
from .models import Author, Genre, Book, Borrow, Reserve

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'surname', 'birth_date']
    search_fields = ['name', 'surname']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_date', 'stock']
    filter_horizontal = ['authors', 'genres']
    search_fields = ['title']
    autocomplete_fields = ['authors', 'genres']

@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    form = BorrowAdminForm
    list_display = ['user', 'book', 'borrowed_at', 'returned_at', 'returned']
    list_filter = ['returned']
    search_fields = ['user__email', 'book__title']
    autocomplete_fields = ['user', 'book']

@admin.register(Reserve)
class ReserveAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'borrowed_at', 'status']
    list_filter = ['status']
    search_fields = ['user__email', 'book__title']
    autocomplete_fields = ['user', 'book']