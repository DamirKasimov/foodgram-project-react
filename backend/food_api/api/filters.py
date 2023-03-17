import django_filters

from content.models import Tags, Recipe


class ToFrontFilters(django_filters.FilterSet):
    is_favorited = django_filters.CharFilter(method='get_is_favorited')
    is_in_shopping_cart = django_filters.\
        CharFilter(method='get_is_in_shopping_cart')
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        to_field_name='slug',
        field_name='tags__slug',
        lookup_expr='contains'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        queryset = queryset.filter(favorite_recipes__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        queryset = queryset.filter(recipes_to_shop__user=user)
        return queryset
