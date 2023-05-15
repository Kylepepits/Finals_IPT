from django.urls import path
from . import views
from .views import BookCreateView, BookListView, UserBookRentalsListView, UserListView,rent_book, return_book
urlpatterns = [
    path('user/', views.get_user),
    path('login/', views.login),
    path('register/', views.register),
    path('logout/', views.logout, name='logout'),
    path('books/create/', BookCreateView.as_view(), name='book_create'),
    # path('rentals/create/', RentBookView.as_view()),
    path('users/', UserListView.as_view(), name='user-list'),
    path('books/', BookListView.as_view(), name='book-list'),  
    path('books/<int:book_id>/rent/', rent_book, name='rent_book'),
    path('users/<int:user_id>/books/', UserBookRentalsListView.as_view()),
    path('books/<int:book_id>/return/', return_book, name='return_book')
]
