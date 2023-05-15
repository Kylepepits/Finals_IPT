from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserRentalSerializer,UserSerializer, BookSerializer
from .models import Book, Rental
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status




def serialize_user(user):
    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }

@api_view(['POST'])
def login(request):
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)
    return Response({
        'user_data': serialize_user(user),
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data['refresh_token']
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'})
    except Exception:
        return Response({'message': 'Failed to logout'}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user_info": serialize_user(user),
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        })


@api_view(['GET'])
def get_user(request):
    user = request.user
    if user.is_authenticated:
        return Response({
            'user_data': serialize_user(user)
        })
    return Response({})

class BookCreateView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer




@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def rent_book(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({"error": "Book not found."}, status=404)

    if not book.available:
        return Response({"error": "Book is already rented."}, status=400)

    rental_date = timezone.now()
    return_date = rental_date + timezone.timedelta(days=3)
    rental = Rental(book=book, user=request.user, rental_date=rental_date, return_date=return_date)
    rental.save()

    book.available = False
    book.save()

    return Response({"success": f"Book {book.title} rented successfully."}, status=200)

class UserBookRentalsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        rentals = Rental.objects.filter(user__id=user_id)
        books = [rental.book for rental in rentals]
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def return_book(request, book_id):
    try:
        rental = Rental.objects.get(book_id=book_id, user=request.user, returned=False)
    except Rental.DoesNotExist:
        return Response({"error": "Rental not found."}, status=404)

    rental.returned = True
    rental.return_date = timezone.now()
    rental.save()

    book = rental.book
    book.available = True
    book.save()

    return Response({"success": f"Book {book.title} returned successfully."}, status=200)

    
