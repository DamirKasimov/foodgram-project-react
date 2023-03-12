from django.urls import include, path
from rest_framework import routers

from .views import RecipeViewSet, TagsViewSet, IngridientsViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngridientsViewSet, basename='ingridients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
]
