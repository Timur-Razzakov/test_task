import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

User = get_user_model()


class UserViewTests(APITestCase):
    """Создаём тестовые данные"""

    def setUp(self):
        # не удалось сохранить при получении токена, поэтому вручную прописал
        self.token = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWN'
                      'jZXNzIiwiZXhwIjoxNjk4MTgyNzY0LCJpYXQiOjE2OTgxNzU1NjQsImp0aSI'
                      '6ImM4YjAzMzBjMGZhMTRlN2NhOGNkZmEyYzZmOWM2OTNkIiwidXNlcl9pZCI6'
                      'MX0.GzqgiehW_9VyqAWOk-CbrjMqitvgk12EyKVuS9krlLI')
        self.auth = self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.user_data = {
            'username': 'A-timur',
            'email': 'timur@gmail.com',
            'password': 'testpassword',
        }
        self.user_data_1 = {
            'username': 'rumit',
            'email': 'timur_01@gmail.com',
            'password': 'testpassword',
        }

        # создаём пользователя и хешируем пароль
        user = User(**self.user_data)
        user.set_password(self.user_data['password'])
        user.save()

        self.user_1 = User.objects.create(**self.user_data_1)

        self.user_data_2 = {
            'username': 'nikita',
            'email': 'nikita@gmail.com',
            'password': 'testpassword',
        }

    def test_user_signup(self):
        """Создаём пользователя"""
        response = self.client.post('/api/signup/', self.user_data_2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        response = self.client.post('/api/login/', {
            'email': 'timur@gmail.com',
            'password': 'testpassword',
        })
        # Получаем и сохраняем access токен
        self.global_variable = response.data['tokens']['access']
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_user_data(self):
        auth = self.auth
        response = self.client.get('/api/all_users/')
        self.assertEqual(response.status_code, 200)

    def test_get_user(self):
        """Получаем пользователя"""
        auth = self.auth
        response = self.client.get(f'/api/all_users/{self.user_1.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_1.email)

    def test_update_user(self):
        """Обновляем пользователя"""

        url = reverse('edit_user', args=[self.user_1.id])
        updated_data = {
            'username': 'newtimur',
            'email': 'newtimur@gmail.com',
        }
        auth = self.auth
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_1.refresh_from_db()
        self.assertEqual(self.user_1.username, updated_data['username'])
        self.assertEqual(self.user_1.email, updated_data['email'])

    def test_delete_user(self):
        """Удаляем пользователя"""
        auth = self.auth
        url = reverse('edit_user', args=[self.user_1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user_1.id).exists())

    def test_search_users_by_username(self):
        """ищем пользователя по имени"""
        auth = self.auth
        url = reverse('search', args=[self.user_1.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, является ли ответ одним словарем
        self.assertTrue(isinstance(response.data, dict))
