import logging

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection, IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter

from api.serializers import LoginSerializer
from api.tokens import create_jwt_pair_for_user

User = get_user_model()

# Создайте логгер
logger = logging.getLogger(__name__)


# Создаём CRUD используя SQL запросы
class CreateUserView(APIView):
    """Создание пользователя"""
    permission_classes = []

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        # Кешируем пароль
        hashed_password = make_password(password)

        # получаем время для добавления в created_at
        current_datetime = timezone.now()

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO api_myuser (username, email, password,created_at,is_admin, "
                "is_superuser) VALUES (%s, %s, %s, %s,%s,%s)",
                [username, email, hashed_password, current_datetime, False, False]
            )
        logger.info('Successful created user', )
        return Response({"message": "User Created Successfully"}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Создаем SQL-запрос для аутентификации пользователя
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username,password FROM api_myuser WHERE email = %s ", [email])
            user_data = cursor.fetchone()
        if user_data:
            # проряем пользователя и его данные
            user = authenticate(request, email=email, password=password)
            if user is not None:
                # Создаем токен для авторизации
                tokens = create_jwt_pair_for_user(user)
                logger.info(f'Successful created token for user')
                response_data = {"message": "Login Successfully", "tokens": tokens}
                return Response(data=response_data, status=status.HTTP_200_OK)
            else:
                logger.error(f'Invalid email or password for user: {email}')
                return Response(data={"message": "Invalid email or password"},
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(data={"message": "User is not found"},
                            status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        # Выводим информацию об авторизованном пользователе
        if request.user.is_authenticated:
            content = {"user": str(request.user), "auth": str(request.auth)}
            return Response(data=content, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "User is not authenticated"},
                            status=status.HTTP_401_UNAUTHORIZED)


class GetAllUsersView(APIView):
    """Получаем всех пользователей"""
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['username', 'email']

    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email FROM api_myuser")
            users_data = cursor.fetchall()

        users = []
        for user_data in users_data:
            user = {
                "id": user_data[0],
                "username": user_data[1],
                "email": user_data[2],
            }
            users.append(user)

        return Response(users, status=status.HTTP_200_OK)


class GetUserView(APIView):
    """Получаем пользователя"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email FROM api_myuser WHERE id = %s",
                [pk]
            )
            user_data = cursor.fetchone()

        if user_data:
            user = {
                "id": user_data[0],
                "username": user_data[1],
                "email": user_data[2],
            }
            return Response(user, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class UpdateUserView(APIView):
    """Обновление пользователя"""
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        hashed_password = make_password(password)
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "UPDATE api_myuser SET username = %s, email = %s, password = %s WHERE id = %s",
                    [username, email, hashed_password, pk]
                )
                return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)
            except IntegrityError as e:
                return Response({"message": "Failed to update user"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    """даление пользователя"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM api_myuser WHERE id = %s",
                [pk]
            )
            if cursor.rowcount > 0:
                return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
            else:
                logger.info(f' User not found with pk: %s', pk)
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class SearchUserView(APIView):
    """Поиск пользователя по имени"""
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email FROM api_myuser WHERE username = %s",
                [username]
            )
            user_data = cursor.fetchone()

        if user_data:
            user = {
                "id": user_data[0],
                "username": user_data[1],
                "email": user_data[2],
            }
            return Response(user, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
