from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import ToFrontFilters
from content.models import (Favorites, IngridientRecipe, Recipe,
                            Shopping_cart, Ingridient, Tags)
from .serializers import (FavoriteSerializer, IngridientsSerializer,
                          RecipeCreateSerializer, RecipePatchSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagsSerializer)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class IngridientsViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Ingridient.objects.all()
    serializer_class = IngridientsSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = ToFrontFilters
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        elif self.action == 'partial_update':
            return RecipePatchSerializer
        else:
            return RecipeSerializer

    # для редактирования Списка покупок
    @action(methods=['post', 'delete'], detail=True,
            serializer_class=ShoppingCartSerializer)
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            # проверка, есть ли уже рецепт в Списке покупок
            if (Shopping_cart.objects.filter(recipe_to_shop=pk,
                                             user=request.user.id).exists()):
                return Response({'errors': 'Рецепт уже в Списке покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                # 3 Версия
                data = Recipe.objects.get(id=pk).__dict__
                serializer = ShoppingCartSerializer(
                    data=data,
                    context={'recipe_to_shop': pk,
                             'user': request.user.id})
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        try:
            Shopping_cart.objects.get(recipe_to_shop=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Shopping_cart.DoesNotExist:
            return Response({'errors': 'Рецепт отсутствует в Списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)

    # декоратор @action + 'favorite' == эндпойнт для работы с избранным
    @action(methods=['post', 'delete'], detail=True,
            serializer_class=FavoriteSerializer)
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            # проверка, есть ли уже рецепт в Избранном
            if (Favorites.objects.filter(favorite_recipe=pk,
                                         user=request.user.id).exists()):
                return Response({'errors': 'Рецепт уже в Избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = FavoriteSerializer(data={'user': request.user.id,
                                                'favorite_recipe': pk})
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        try:
            Favorites.objects.get(favorite_recipe=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Favorites.DoesNotExist:
            return Response({'errors': 'Рецепт отсутствует в Избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

    # путь /recipes/ скачать файл списка покупок
    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        result = IngridientRecipe.objects.select_related('ingredient').\
            filter(recipe_id__in=Shopping_cart.objects.
                   values('recipe_to_shop_id'))
        totals = result.values('ingredient_id__name',
                               'ingredient_id__measurement_unit').\
            annotate(totals=Sum('amount'))
        content = ''
        for item in totals:
            name = (item['ingredient_id__name'][0]).\
                upper()+(item['ingredient_id__name'])[1:]
            item['ingredient_id__name'] = name
            name = item['ingredient_id__name']
            measure = item['ingredient_id__measurement_unit']
            total = item['totals']
            content += f'{name} ({measure}) -- {total}\n'
        return HttpResponse(content, content_type='text/plain',
                            status=status.HTTP_200_OK)
