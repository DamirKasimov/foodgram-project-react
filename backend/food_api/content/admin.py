from django.contrib import admin

from .models import (Favorites, Ingridient, IngridientRecipe, Recipe,
                     Tags)
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', '__str__',)
    list_filter = ('email', 'username',)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)


@admin.register(Ingridient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', '__str__',)


@admin.register(IngridientRecipe)
class IngridientRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__')
