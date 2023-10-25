import logging

from django.contrib.auth import authenticate, get_user_model
from django.db.models import F, Value, CharField
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated)
from rest_framework.filters import OrderingFilter

from .serializers import SignUpSerializer, UserListSerializer, LoginSerializer, UpdateSerializer
from .tokens import create_jwt_pair_for_user

User = get_user_model()

# Создайте логгер
logger = logging.getLogger(__name__)


#  python manage.py spectacular --file schema.yml

# TODO: filter and sort user
# TODO: Check RESTFULL API
# TODO: Readme
# TODO: PEP8 check
# TODO: check show swagger

class SignUpView(generics.GenericAPIView):
    """Проводим регистрацию"""
    serializer_class = SignUpSerializer
    permission_classes = []

    def post(self, request: Request):
        data = request.data

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            logger.info('Successful created user:  %s', serializer.data)
            response = {"message": "User Created Successfully", "data": serializer.data}

            return Response(data=response, status=status.HTTP_201_CREATED)
        logger.error('serializer is not valid:  %s', serializer.data)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Получаем токен, для авторизации"""
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                # создаём токен для авторизации
                tokens = create_jwt_pair_for_user(user)
                logger.info('Successful created token for user:  %s', user)
                response = {"message": "Login Successfully", "tokens": tokens}
                return Response(data=response, status=status.HTTP_200_OK)
            else:
                logger.error('Invalid email or password for user:  %s', email)
                return Response(data={"message": "Invalid email or password"},
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            logger.error('Invalid data received for login')
            return Response(data={"message": "Invalid data received for login"},
                            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # выводим информацию об авторизованном пользователе
        content = {"user": str(request.user), "auth": str(request.auth)}

        return Response(data=content, status=status.HTTP_200_OK)


class ListUsersView(generics.ListAPIView):
    """Выводим пользователей"""
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]  # IsAuthenticated
    # сортируем по имени и почте
    queryset = User.objects.annotate(
        lower_username=F('username'),
    ).values(
        'id',
        'username',
        'email',
    ).annotate(
        order=Value('', CharField()),
    ).order_by('order')
    filter_backends = [OrderingFilter]
    ordering_fields = ['username', 'email']

    def get_queryset(self):
        return User.objects.all()


#

class UserView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование пользователя"""
    serializer_class = UpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()


class UserSearchView(APIView):
    """Поиск по имени"""
    permission_classes = [IsAuthenticated]

    # для избавления от ошибки 'unable to guess serializer' при использовании swagger-ра
    @extend_schema(responses=LoginSerializer)
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            return Response({"username": user.username, "email": user.email}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error('The user is empty: UserSearchView %s ', user.username)
            return Response({"message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
