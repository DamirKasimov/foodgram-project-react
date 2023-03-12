from django.db import models
from django.core.validators import MinValueValidator
from users.models import User


TAG_NAME_CHOICES = [
    ('Завтрак', 'Завтрак'),
    ('Обед', 'Обед'),
    ('Ужин', 'Ужин'),
]
TAG_SLUG_CHOICES = [
    ('Breakfast', 'Breakfast'),
    ('Dinner', 'Dinner'),
    ('Supper', 'Supper'),
]
TAG_COLOR_CHOICES = [
    ('#FF6600', 'Оранжевый'),
    ('#44944A', 'Зеленый'),
    ('#9966CC', 'Фиолетовый'),
]


class Tags(models.Model):
    name = models.CharField(
        choices=TAG_NAME_CHOICES,
        max_length=20
    )
    slug = models.SlugField(
        choices=TAG_SLUG_CHOICES
    )
    color = models.CharField(
        choices=TAG_COLOR_CHOICES,
        max_length=20
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingridient(models.Model):
    name = models.CharField(
        max_length=100
    )
    measurement_unit = models.CharField(
        max_length=20
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngridientRecipe(models.Model):
    """Класс для связи ингредентов и рецептов, M2M"""
    ingredient = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Рецепт',
        null=True
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте М2М'

    def __str__(self):
        return f'Кол-во {self.amount}'


class Recipe(models.Model):
    """Класс рецептов"""
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(upload_to='recipes/images/',
                              null=True, blank=True)
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingridient,
        through=IngridientRecipe,
        related_name='recipes',
        verbose_name='Ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='recipes',
        verbose_name='Тэг'
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Время приготовления (мин.)'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:20]


class Favorites(models.Model):
    """Класс Избранное"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites",
        null=True, blank=True,)
    favorite_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite_recipes",
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-user"]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил {self.favorite_recipe} себе в Избранное'


class Shopping_cart(models.Model):
    """Список покупок"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_cart",
        null=True, blank=True,)
    recipe_to_shop = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipes_to_shop",
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["-user"]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe_to_shop} в Список покупок'
