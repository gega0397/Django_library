from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView

from Django_final.emailing import email
from books.forms import BookForm
from books.models import Book, Reserve, Borrow, Genre
from books.paginators import CustomPageNumberPagination


class MyListView(LoginRequiredMixin, ListView):

    def my_context_data(self, title, **kwargs):
        page_range = settings.PAGE_PAGINATION_VIEW_COUNT
        context = super().get_context_data(**kwargs)
        context['form'] = BookForm(self.request.GET)
        context['title'] = title
        context['prev_pages'] = []
        context['next_pages'] = []

        paginator = Paginator(self.object_list, settings.DEFAULT_PAGE_SIZE)
        page = self.request.GET.get('page')
        if page is None or not page.isdigit() or int(page) < 1 or int(page) > paginator.num_pages:
            page = 1
        else:
            page = int(page)

        if page > 1:
            context['prev_pages'] = list(range(max(1, int(page) - page_range), int(page)))
        if page < paginator.num_pages:
            context['next_pages'] = list(range(int(page) + 1, min(int(page) + page_range, paginator.num_pages + 1)))

        try:
            books = paginator.page(page)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        context['books'] = books

        return context


class HomeView(MyListView):
    model = Book
    template_name = 'books/home.html'
    queryset = Book.objects.all()
    title = 'Home'

    def get_context_data(self, **kwargs):
        return self.my_context_data('Home', **kwargs)


class BookSearchView(MyListView):
    model = Book
    template_name = 'books/books.html'

    def get_queryset(self):
        query = self.request.GET.get('query', None)
        genre_id = self.request.GET.get('genre', None)
        queryset = Book.objects.all()

        if query:
            queryset = queryset.filter(title__icontains=query)
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)

        return queryset

    def get_context_data(self, **kwargs):
        return self.my_context_data('Home', **kwargs)


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BookForm(self.request.GET)
        book = self.object
        borrows_count = book.borrows.filter(returned=False).count()
        reserves_count = book.reserves.filter(status=True).count()
        available_to_borrow = book.stock > borrows_count + reserves_count if book.stock > 0 else False
        user = self.request.user

        user_reserved_book = Reserve.objects.filter(user=user, book=book, status=True).exists()

        context['borrows_count'] = borrows_count
        context['reserves_count'] = reserves_count
        context['available_to_borrow'] = available_to_borrow
        context['user_reserved_book'] = user_reserved_book

        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')
        book = self.get_object()
        if form_type == 'reserve_form':
            # book = self.get_object()
            print("Book ID:", book.pk)
            if not Reserve.objects.filter(user=request.user, book=book, status=True).exists():
                try:
                    reserve = Reserve.objects.create(user=request.user, book=book)
                    reserve.save()
                except ValidationError as e:
                    print("Validation error:", e)
                except Exception as e:
                    print("An error occurred:", e)
            return redirect('books:book_detail', pk=book.pk)
        if form_type == 'reserve_cancel_form':
            reserve = Reserve.objects.get(user=request.user, book=book, status=True)
            reserve.status = False
            reserve.save()
            #email(request)
            return redirect('books:book_detail', pk=book.pk)


class FilteredBorrowListView(MyListView):
    model = Borrow
    template_name = 'books/book_list.html'
    context_object_name = 'borrows'

    filter_conditions = {
        'history': {'returned': True},
        'not_due': {'due_date__gte': timezone.now(), 'returned': False},
        'due': {'due_date__lt': timezone.now(), 'returned': False},
    }

    def get_filter_type(self):
        return self.request.GET.get('filter_type')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)

        filter_type = self.get_filter_type()
        if filter_type and filter_type in self.filter_conditions:
            queryset = queryset.filter(**self.filter_conditions[filter_type])

        return queryset

    def get_context_data(self, **kwargs):
        return self.my_context_data('Home', **kwargs)



class FilteredReservedBooksView(MyListView):
    model = Reserve
    template_name = 'books/book_list.html'
    context_object_name = 'borrows'

    filter_conditions = {
        'active': {'status': True},
        'history': {'status': False},
    }

    def get_filter_type(self):
        return self.request.GET.get('filter_type')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)

        filter_type = self.get_filter_type()
        if filter_type and filter_type in self.filter_conditions:
            queryset = queryset.filter(**self.filter_conditions[filter_type])

        return queryset

    def get_context_data(self, **kwargs):
        return self.my_context_data('Home', **kwargs)

class GenreListView(ListView):
    model = Genre
    template_name = 'books/genres.html'
    context_object_name = 'genres'
    paginate_by = settings.PAGE_PAGINATION_VIEW_COUNT

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Genres'
        return context
