# CRUD user сервис

Сервис разработан на django rest framework
````
Есть 2 ветки, в одной для обращения к базе данных были использованы SQL запросы(with_sql_requests,
 а в другой ORM django (master)

````

## Запуск тестов

Перейдите в корневую директорию и пропишите

````
python manage.py test

````

## Установка и запуск

1. Склонировать репозиторий с Github:

````
git clone https://github.com/Timur-Razzakov/test_task.git
````

2. Перейти в директорию проекта

3. Создать виртуальное окружение:

````
python -m venv venv
````

4. Активировать окружение (Linux):

````
source\venv\bin\activate
````

5. В файле .evn заполнить необходимые данные

```
SECRET_KEY=
DEBUG=
DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 0.0.0.0 [::1]

```

6. Установка зависимостей:

```
pip install -r requirements.txt
```

7. Создать и применить миграции в базу данных:

```
python manage.py makemigrations
python manage.py migrate
```

8. Запустить сервер

```
python manage.py runserver 0.0.0.0:8000
```

***

# Установка проекта с помощью docker-compose

Проверить наличие Docker-ра и docker-compose

```
sudo docker ps
```

Если нет, можно установить по ссылке ниже

```

https://docs.docker.com/engine/install/

```

4. Запустить контейнер, можно перейдя в корневую директорию и прописать

``` 
sudo docker-compose up 
 ```

5. Остановка работы контейнера

```
sudo docker-compose stop
```

# API

***
```http://127.0.0.1:8000/api/registration/``` - регистрация

```http://127.0.0.1:8000/api/authorization/``` - авторизация пользователей, путём получения токена

```http://0.0.0.0:8000/users_list/``` - Выводим всех пользователей

```http://0.0.0.0:8000/users_list/<int:pk>``` - Выводим указанного пользователя по id

```http://0.0.0.0:8000/users_list/<int:pk>``` - Удаление пользователя

```http://0.0.0.0:8000/users_list/<str:username>``` - Ищем пользователя по имени

```http://0.0.0.0:8000/users_list/ordering:username>``` - Сортировка по имени

```http://0.0.0.0:8000/users_list/ordering:-username>``` - Сортировка по имени в обратном порядке

```http://0.0.0.0:8000/users_list/ordering:mail>``` - Сортировка по почте

```http://0.0.0.0:8000/users_list/ordering:-mail>``` - Сортировка по почте в обратном порядке

```http://0.0.0.0:8000/jwt/create/``` - Создаём токен для пользователя

```http://0.0.0.0:8000/jwt/refresh/``` - Обновляем токен

```http://0.0.0.0:8000/jwt/verify/``` - Проверка работоспособности токена

```http://0.0.0.0:8000/api/schema/docs/``` - документация проекта

***
