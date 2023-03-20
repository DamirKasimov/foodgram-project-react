from django.urls import include, path
from rest_framework import routers

from .views import RecipeViewSet, TagsViewSet, IngridientsViewSet
from users.views import CustomUserViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngridientsViewSet, basename='ingridients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    # + /?recipes_limit=...
    path('users/subscriptions/', CustomUserViewSet.as_view(
        {'get': 'subscriptions'}), name='subscriptions'),
    # re_path(r'(/users/)?', include('djoser.urls')),
    # + /?recipes_limit=...
    path('users/<int:id>/subscribe/', CustomUserViewSet.as_view(
        {'post': 'subscribe', 'delete': 'subscribe'}), name='to_un/subscribe'),
]
