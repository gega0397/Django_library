from datetime import timedelta

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView, View
from rest_framework import generics, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from users.choices import UserTypeChoices

from books.models import Author, Genre, Book, Borrow, Reserve
from books.serializers import (BookSerializer,
                               AuthorSerializer,
                               GenreSerializer,
                               AuthorDetailsSerializer,
                               GenreDetailsSerializer,
                               ReserveStatusUpdateSerializer,
                               ReserveSerializer,
                               BorrowStatusUpdateSerializer,
                               BorrowSerializer,
                               CreateBookSerializer,
                               BorrowCreateSerializer,
                               ReserveCreateSerializer, CustomTokenObtainPairSerializer, TopBookSerializer,
                               TopWorstUserSerializer,
                               )
from django.shortcuts import render
from books.paginators import CustomPageNumberPagination
from django.db.models import Count, Case, When, IntegerField, Prefetch, F
from rest_framework.response import Response
from books.view_permissions import CreatePermissions, CreateUpdateReserveBorrow
from users.models import CustomUser


class AtomicCreateAPIView(generics.CreateAPIView):
    permission_classes = [CreatePermissions]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AtomicRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [CreatePermissions]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class AuthListAPIView(generics.ListAPIView):
    authentication_classes = [SessionAuthentication, JWTAuthentication]


class AuthorCreateView(AtomicCreateAPIView):
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()


class GenreCreateView(AtomicCreateAPIView):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class BookCreateView(AtomicCreateAPIView):
    serializer_class = CreateBookSerializer
    queryset = Book.objects.all()


class AuthorBatchCreateView(AtomicCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GenreBatchCreateView(AtomicCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookBatchCreateView(AtomicCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = CreateBookSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookListAPIView(AuthListAPIView):
    serializer_class = BookSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Book.objects.prefetch_related(
            'authors',
            'genres',
            'borrows'
        ).annotate(
            borrows_count=Count(
                Case(
                    When(borrows__returned=False, then=1),
                    output_field=IntegerField()
                )
            ),
            reserves_count=Count(
                Case(
                    When(reserves__status=True, then=1),
                    output_field=IntegerField()
                )
            )
        )
        author_ids = self.request.query_params.getlist('authors')
        genre_ids = self.request.query_params.getlist('genres')

        if author_ids:
            author_ids = [int(author_id) for author_id in author_ids]
            queryset = queryset.filter(authors__id__in=author_ids)
        if genre_ids:
            genre_ids = [int(genre_id) for genre_id in genre_ids]
            queryset = queryset.filter(genres__id__in=genre_ids)

        queryset = queryset.order_by('id')

        return queryset


class BookDetailsAPIView(AtomicRetrieveUpdateAPIView):
    queryset = Book.objects.prefetch_related(
        'authors',
        'genres',
        'borrows'
    ).annotate(
        borrows_count=Count(
            Case(
                When(borrows__returned=False, then=1),
                output_field=IntegerField()
            )
        ),
        reserves_count=Count(
            Case(
                When(reserves__status=True, then=1),
                output_field=IntegerField()
            )
        )
    )
    serializer_class = BookSerializer


class AuthorListAPIView(AuthListAPIView):
    serializer_class = AuthorSerializer
    pagination_class = CustomPageNumberPagination
    queryset = Author.objects.all().order_by('id')


class AuthorDetailAPIView(AtomicRetrieveUpdateAPIView):
    queryset = Author.objects.prefetch_related('books').annotate(books_count=Count('books'))
    serializer_class = AuthorDetailsSerializer


class GenreListAPIView(AuthListAPIView):
    serializer_class = GenreSerializer
    pagination_class = CustomPageNumberPagination
    queryset = Genre.objects.all().order_by('id')


class GenreDetailAPIView(AtomicRetrieveUpdateAPIView):
    queryset = Genre.objects.prefetch_related('books').annotate(books_count=Count('books'))
    serializer_class = GenreDetailsSerializer


class ReserveDetailView(AtomicRetrieveUpdateAPIView):
    queryset = Reserve.objects.all().order_by('id')

    # permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return ReserveStatusUpdateSerializer
        return ReserveSerializer


class BorrowDetailView(AtomicRetrieveUpdateAPIView):
    queryset = Borrow.objects.all()

    # permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return BorrowStatusUpdateSerializer
        return BorrowSerializer


class BorrowListAPIView(AuthListAPIView):
    serializer_class = BorrowSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Borrow.objects.all().prefetch_related('user', 'book').filter(returned=False)
        if self.request.user.user_type == str(UserTypeChoices.STUDENT):
            queryset = queryset.filter(user=self.request.user)
        queryset = queryset.order_by('due_date')
        return queryset


class BorrowHistoryListAPIView(AuthListAPIView):
    serializer_class = BorrowSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Borrow.objects.all().prefetch_related('user', 'book').filter(returned=True)
        if self.request.user.user_type == str(UserTypeChoices.STUDENT):
            queryset = queryset.filter(user=self.request.user)
        queryset = queryset.order_by('due_date')
        return queryset


class ReserveListAPIView(AuthListAPIView):
    serializer_class = ReserveSerializer
    pagination_class = CustomPageNumberPagination
    ordering_fields = ['due_date']
    ordering = ['-due_date']

    def get_queryset(self):
        queryset = Reserve.objects.all().prefetch_related('user', 'book').filter(status=True)
        if self.request.user.user_type == str(UserTypeChoices.STUDENT):
            queryset = queryset.filter(user=self.request.user)
        queryset = queryset.order_by('due_date')
        return queryset


class ReserveHistoryListAPIView(AuthListAPIView):
    serializer_class = ReserveSerializer
    pagination_class = CustomPageNumberPagination
    ordering_fields = ['due_date']
    ordering = ['-due_date']

    def get_queryset(self):
        queryset = Reserve.objects.all().prefetch_related('user', 'book').filter(status=False)
        if self.request.user.user_type == str(UserTypeChoices.STUDENT):
            queryset = queryset.filter(user=self.request.user)
        queryset = queryset.order_by('due_date')
        return queryset


class BorrowCreateView(AtomicCreateAPIView):
    queryset = Borrow.objects.all()
    serializer_class = BorrowCreateSerializer

    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        book = request.data.get('book')

        active_borrow = Borrow.objects.filter(user=user, book=book, returned=False).first()

        if active_borrow:
            return Response({"error": "There is already an active borrow on this book."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReserveCreateView(AtomicCreateAPIView):
    queryset = Reserve.objects.all()
    serializer_class = ReserveCreateSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        book = request.data.get('book')
        if user != str(request.user.id):
            return Response({"error": "can only reserve for yourself."},
                            status=status.HTTP_400_BAD_REQUEST)

        active_reserve = Reserve.objects.filter(user=user, book=book, status=True).first()

        if active_reserve:
            return Response({"error": "There is already an active reservation on this book."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookSearchView(View):
    authentication_classes = [SessionAuthentication, JWTAuthentication]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')

        search_results = Book.objects.filter(title__icontains=query)

        results_list = [book.title for book in search_results]
        return JsonResponse({'results': results_list})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class StatisticsTopBookListAPIView(AuthListAPIView):
    serializer_class = TopBookSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Book.objects.prefetch_related(
            'borrows'
        ).annotate(borrows_count=Count('borrows')).order_by('-borrows_count')

        queryset = queryset.order_by('-borrows_count')[:10]

        return queryset


class StatisticsBookBorrowsListAPIView(AuthListAPIView):
    serializer_class = TopBookSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        delta = timezone.now() - timedelta(days=365)
        queryset = Book.objects.prefetch_related(
            'borrows'
        ).annotate(
            borrows_count=Count(
                Case(
                    When(borrows__borrowed_at__gte=delta, then=1),
                    output_field=IntegerField()
                )
            )
        )

        return queryset


class StatisticsBookBorrowsLateListAPIView(AuthListAPIView):
    serializer_class = TopBookSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Book.objects.prefetch_related(
            'borrows'
        ).annotate(
            borrows_count=Count(
                Case(
                    When(borrows__returned_at__gt=F('borrows__due_date'), then=1),
                    output_field=IntegerField()
                )
            )
        )
        queryset = queryset.order_by('-borrows_count')[:100]
        return queryset


class StatisticsBookBorrowsLateListAPIView(AuthListAPIView):
    serializer_class = TopWorstUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        delta = timezone.now() - timedelta(days=365)
        queryset = CustomUser.objects.prefetch_related(
            'borrows'
        ).annotate(
            borrows_count=Count(
                Case(
                    When(borrows__returned_at__gt=F('borrows__due_date'), then=1),
                    output_field=IntegerField()
                )
            )
        )
        queryset = queryset.order_by('-borrows_count')[:100]
        return queryset
