from django.contrib.auth import authenticate, get_user_model, login
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)
from .serializers import SignUpSerializer, UserListSerializer
from .tokens import create_jwt_pair_for_user

User = get_user_model()


class SignUpView(generics.GenericAPIView):
    serializer_class = SignUpSerializer
    permission_classes = []

    def post(self, request: Request):
        data = request.data

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()

            response = {"message": "User Created Successfully", "data": serializer.data}

            return Response(data=response, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = []

    def post(self, request: Request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(email=email, password=password)
        if user is not None:
            # создаём токен для авторизации
            tokens = create_jwt_pair_for_user(user)
            response = {"message": "Login Successfull", "tokens": tokens}
            return Response(data=response, status=status.HTTP_200_OK)

        else:
            return Response(data={"message": "Invalid email or password"})

    def get(self, request: Request):
        # выводим информацию об авторизованном пользователе
        content = {"user": str(request.user), "auth": str(request.auth)}

        return Response(data=content, status=status.HTTP_200_OK)


class ListUsersView(generics.ListAPIView):
    """Выводим пользователей"""
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]  # IsAuthenticated

    def get_queryset(self):
        return User.objects.all()


class UserView(generics.RetrieveUpdateDestroyAPIView):
    """Редактирование пользователя"""
    serializer_class = SignUpSerializer
    permission_classes = [IsAuthenticated]  #

    def get_queryset(self):
        return User.objects.all()


class UserSearchView(APIView):
    """Поиск по имени"""
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            return Response({"username": user.username, "email": user.email}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
