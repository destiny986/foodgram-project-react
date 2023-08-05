from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        max_length=320,
        unique=True,
        blank=False,
        null=False,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=255,
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        'Имя',
        max_length=255,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=255,
        blank=False,
        null=False
    )
    password = models.CharField(
        'Пароль',
        max_length=255,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
