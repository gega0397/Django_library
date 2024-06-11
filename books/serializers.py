from rest_framework import serializers
from books.models import Author, Genre, Book, Borrow, Reserve
from users.models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name']
        depth = 1


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'surname', 'birth_date']
        depth = 1


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']
        depth = 1


class BorrowSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Borrow
        fields = ['id', 'user', 'borrowed_at', 'due_date', 'returned']
        depth = 1


class CreateBookSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True, write_only=True)
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True, write_only=True)

    class Meta:
        model = Book
        fields = ['title', 'authors', 'genres', 'release_date', 'stock']

    def create(self, validated_data):
        authors = validated_data.pop('authors', [])
        genres = validated_data.pop('genres', [])
        book = Book.objects.create(**validated_data)
        book.authors.set(authors)
        book.genres.set(genres)
        return book


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, required=False)
    genres = GenreSerializer(many=True, required=False)
    available_to_borrow = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'release_date', 'stock', 'available_to_borrow']

    def get_available_to_borrow(self, obj):
        # print(obj.stock, obj.borrows_count)
        return obj.stock > obj.borrows_count + obj.reserves_count if obj.stock > 0 else False


class TopBookSerializer(serializers.ModelSerializer):
    borrows_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'genres', 'release_date', 'stock', 'borrows_count']

    def get_borrows_count(self, obj):
        # print(obj.stock, obj.borrows_count)
        return obj.borrows_count


class TopWorstUserSerializer(serializers.ModelSerializer):
    borrows_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'borrows_count']

    def get_borrows_count(self, obj):
        # print(obj.stock, obj.borrows_count)
        return obj.borrows_count


class AuthorDetailsSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    books_link = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'surname', 'birth_date', 'book_count', 'books_link']

    def get_book_count(self, obj):
        return obj.books_count

    def get_books_link(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f'/api/books/?authors={obj.id}')


class GenreDetailsSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    books_link = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ['id', 'name', 'book_count', 'books_link']

    def get_book_count(self, obj):
        return obj.books_count

    def get_books_link(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(f'/api/books/?genres={obj.id}')


class ReserveSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Reserve
        fields = ['user', 'book', 'borrowed_at', 'due_date', 'status']


class ReserveStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserve
        fields = ['status']


class BorrowStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['returned']


class BorrowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['user', 'book', 'due_date']


class ReserveCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserve
        fields = ['user', 'book']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims if needed
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Use 'email' instead of 'username'
        attrs['username'] = attrs.get('email')
        return super().validate(attrs)
