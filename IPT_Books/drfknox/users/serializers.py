from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers, validators
from .models import Book, Rental


class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ("id","username", "password", "email", "first_name", "last_name")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {
                "required": True,
                "allow_blank": False,
                "validators": [
                    validators.UniqueValidator(
                        queryset=User.objects.all(), message="A user with that Email already exists."
                    )
                ],
            },
        }

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email'),
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            is_staff=True, 
        )
        user.set_password(validated_data.get('password'))
        user.save()

        return user


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'description', 'price', 'available', 'created_at', 'updated_at','image')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class RentalSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.filter(available=True))
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    rental_date = serializers.DateTimeField(read_only=True)
    return_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Rental
        fields = ['id', 'book', 'user', 'rental_date', 'return_date']

    def create(self, validated_data):
        book = validated_data['book']
        rental_date = timezone.now()
        return_date = rental_date + timezone.timedelta(days=3)
        rental = Rental.objects.create(book=book, user=self.context['request'].user, rental_date=rental_date, return_date=return_date)
        book.available = False
        book.save()
        return rental


class UserRentalSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    rental_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Rental
        fields = ['book', 'rental_date', 'return_date']
