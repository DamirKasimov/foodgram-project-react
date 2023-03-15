from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомизирует пользовательский класс."""

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    class Meta:
        """
        Сортирует пользователей и добавляет русские название в админке.
        """
        ordering = ('-id', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_follower',
        verbose_name='Подписчик'
    )
    followed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscription_followed',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['follower', 'followed'],
                                        name='subscription_uniqueness'),
                models.CheckConstraint
                (name='self_follow_not',
                 check=~models.Q(followed=models.F("follower")))
                ]
