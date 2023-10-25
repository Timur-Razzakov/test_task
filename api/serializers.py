from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import ValidationError

from .models import MyUser


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=45)
    email = serializers.CharField(max_length=80)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = MyUser
        fields = ["email", "username", "password"]

    def validate(self, attrs):
        email_exists = MyUser.objects.filter(email=attrs["email"]).exists()

        if email_exists:
            raise ValidationError("Email has already been used")

        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = MyUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        Token.objects.create(user=user)

        return user


class LoginSerializer(serializers.ModelSerializer):
    """Для вывода пользователей"""

    class Meta:
        model = MyUser
        fields = ["email", "username"]


class UpdateSerializer(serializers.ModelSerializer):
    """Для редактирования пользователя"""

    class Meta:
        model = MyUser
        fields = ["email", "username", "password"]


class UserListSerializer(serializers.ModelSerializer):
    """Для вывода пользователей"""

    class Meta:
        model = MyUser
        fields = ["id", "email", "username"]
