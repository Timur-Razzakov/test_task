from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserViewTests(APITestCase):
    """Создаём тестовые данные"""
    token = None  # Атрибут для хранения токена
    token_refresh = None  # Атрибут для хранения refresh токена

    def setUp(self):
        self.user_data = {
            'username': 'A-timur',
            'email': 'timur@gmail.com',
            'password': 'testpassword',
        }
        # создаём пользователя и хешируем пароль
        user = User(**self.user_data)
        user.set_password(self.user_data['password'])
        user.save()
        # создаём токен для пользователя
        response = self.client.post(reverse('jwt_create'), {
            'email': self.user_data['email'],
            'password': self.user_data['password']}, format='json')
        # сохраняем access токен для дальнейшего использования
        self.token = response.data['access']
        self.token_refresh = response.data['refresh']

        self.user_data_1 = {
            'username': 'rumit',
            'email': 'B_timur_01@gmail.com',
            'password': 'testpassword',
        }

        self.user_1 = User.objects.create(**self.user_data_1)

        self.user_data_2 = {
            'username': 'nikita',
            'email': 'nikita@gmail.com',
            'password': 'testpassword',
        }

    def test_user_registration(self):
        """Создаём пользователя"""
        url = reverse('registration')
        response = self.client.post(url, self.user_data_2, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_authorization(self):
        """Получаем токен для авторизации"""
        url = reverse('authorization')
        response = self.client.post(url, {
            'email': self.user_data['email'],
            'password': self.user_data['password'],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_data(self):
        """Получаем всех пользователей"""
        # подключаем наш токен
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get('/api/users_list/')
        self.assertEqual(response.status_code, 200)

    def test_get_user_without_token(self):
        """Проверяем получение пользователя без токена"""
        response = self.client.get(f'/api/users_list/{self.user_1.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user(self):
        """Получаем пользователя"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(f'/api/users_list/{self.user_1.id}', follow=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_1.email)

    def test_update_user(self):
        """Обновляем пользователя"""

        url = reverse('users', args=[self.user_1.id])
        updated_data = {
            'username': 'newtimur',
            'email': 'newtimur@gmail.com',
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_1.refresh_from_db()
        self.assertEqual(self.user_1.username, updated_data['username'])
        self.assertEqual(self.user_1.email, updated_data['email'])

    def test_delete_user(self):
        """Удаляем пользователя"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('users', args=[self.user_1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user_1.id).exists())

    def test_search_users_by_username(self):
        """Ищем пользователя по имени"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('search', args=[self.user_1.username])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, является ли ответ одним словарем
        self.assertTrue(isinstance(response.data, dict))

    def test_sort_users_by_name_ascending(self):
        """Сортируем пользователя по имени A-W"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('users_list')
        response = self.client.get(url, {'ordering': 'username'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data]
        # проверяем, что имя с A стоит первым
        self.assertEqual(usernames, ['A-timur', 'rumit'])

    def test_sort_users_by_name_descending(self):
        """Сортируем от W-A"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('users_list')
        response = self.client.get(url, {'ordering': '-username'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data]
        # проверяем, что имя с A стоит первым
        self.assertEqual(usernames, ['rumit', 'A-timur'])

    def test_sort_users_by_email_ascending(self):
        """Сортируем по почте"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('users_list')
        response = self.client.get(url, {'ordering': 'email'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [user['email'] for user in response.data]
        self.assertEqual(emails, ['B_timur_01@gmail.com', 'timur@gmail.com'])

    def test_jwt_refresh(self):
        """Обновляем токен"""
        response = self.client.post(reverse('token_refresh'), {
            'refresh': self.token_refresh, }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_jwt_verify(self):
        """Проверяем действительность токена"""
        response = self.client.post(reverse('token_verify'), {
            'token': self.token, }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
