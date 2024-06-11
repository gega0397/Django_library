from django.urls import path, re_path
from django.views.generic import RedirectView, TemplateView
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from books.views.normal_views import (
    HomeView,
    BookSearchView,
    BookDetailView,
    BorrowedBooksNotDueView,
    BorrowedBooksDueView,
    BorrowHistoryView,
    ActiveReservedBooksView,
    ReservedBooksHistoryView, GenreListView,
)
from books.views.api_views import (
    BookListAPIView,
    AuthorDetailAPIView,
    AuthorListAPIView,
    GenreDetailAPIView,
    GenreListAPIView,
    BookDetailsAPIView,
    ReserveDetailView,
    BorrowDetailView,
    BorrowListAPIView,
    BorrowHistoryListAPIView,
    ReserveListAPIView,
    ReserveHistoryListAPIView,
    AuthorCreateView,
    GenreCreateView,
    BookCreateView,
    AuthorBatchCreateView,
    GenreBatchCreateView,
    BookBatchCreateView,
    BorrowCreateView,
    ReserveCreateView,
    CustomTokenObtainPairView,
    StatisticsTopBookListAPIView,
    StatisticsBookBorrowsListAPIView,
    StatisticsBookBorrowsLateListAPIView
)

app_name = 'books'

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', HomeView.as_view(), name='home'),
    path('search/', BookSearchView.as_view(), name='search'),
    path('<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('genres/', GenreListView.as_view(), name='genre-list-generic'),
    path('borrowed-books-not-due/', BorrowedBooksNotDueView.as_view(), name='not_due_books'),
    path('borrowed-books-due/', BorrowedBooksDueView.as_view(), name='due_books'),
    path('borrow-history/', BorrowHistoryView.as_view(), name='borrow_history'),
    path('active-reserved-books/', ActiveReservedBooksView.as_view(), name='active_reserved_books'),
    path('reserved-books-history/', ReservedBooksHistoryView.as_view(), name='reserved_books_history'),

    path('api/books/', BookListAPIView.as_view(), name='book-list'),
    path('api/books/<int:pk>/', BookDetailsAPIView.as_view(), name='book-detail'),
    path('api/authors/<int:pk>/', AuthorDetailAPIView.as_view(), name='author-detail'),
    path('api/genres/<int:pk>/', GenreDetailAPIView.as_view(), name='genre-detail'),
    path('api/authors/', AuthorListAPIView.as_view(), name='author-list'),
    path('api/genres/', GenreListAPIView.as_view(), name='genre-list'),
    path('api/reserves/<int:pk>/', ReserveDetailView.as_view(), name='reserve-detail'),
    path('api/borrows/<int:pk>/', BorrowDetailView.as_view(), name='borrow-detail'),
    path('api/borrows/', BorrowListAPIView.as_view(), name='borrow-list'),
    path('api/borrows_history/', BorrowHistoryListAPIView.as_view(), name='borrow-history'),
    path('api/reserves/', ReserveListAPIView.as_view(), name='reserve-list'),
    path('api/reserves_history/', ReserveHistoryListAPIView.as_view(), name='reserve-history'),
    path('api/authors/create/', AuthorCreateView.as_view(), name='author-create'),
    path('api/genres/create/', GenreCreateView.as_view(), name='genre-create'),
    path('api/books/create/', BookCreateView.as_view(), name='book-create'),
    path('api/authors/create_batch/', AuthorBatchCreateView.as_view(), name='author-create-batch'),
    path('api/genres/create_batch/', GenreBatchCreateView.as_view(), name='genre-create-batch'),
    path('api/books/create_batch/', BookBatchCreateView.as_view(), name='book-create-batch'),
    path('api/borrows/create/', BorrowCreateView.as_view(), name='borrow-create'),
    path('api/reserves/create/', ReserveCreateView.as_view(), name='reserve-create'),
    path('api/statistics/top-books/', StatisticsTopBookListAPIView.as_view(), name='top-books'),
    path('api/statistics/top-worst-users/', StatisticsBookBorrowsLateListAPIView.as_view(), name='top-worst-users'),
    path('api/statistics/books_borrows/', StatisticsBookBorrowsListAPIView.as_view(), name='top-books-borrows'),
    path('api/statistics/late_returns', StatisticsBookBorrowsLateListAPIView.as_view(), name='late-returns'),
]
