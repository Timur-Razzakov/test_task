from django.contrib import admin
from django.contrib.auth.models import Group

from .models import MyUser


admin.site.register(MyUser)
""" отмена регистрацию модели группы от администратора"""
admin.site.unregister(Group)