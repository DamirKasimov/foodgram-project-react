from content.models import Recipe
from rest_framework import serializers

from .models import User


class NewRecipesSerialaizer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time')


class SubscriptionUserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'email', 'username', 'id', 'last_name')


class SubscriptionSerializer(SubscriptionUserInfoSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(SubscriptionUserInfoSerializer.Meta):
        fields = SubscriptionUserInfoSerializer.Meta.fields +\
            ('is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, object):
        # object == followed_author
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        output = Recipe.objects.filter(author_id=object.id).\
            prefetch_related('ingredients').all()[:int(recipes_limit)]
        return NewRecipesSerialaizer(output, many=True).data

    def get_is_subscribed(self, instance):
        return True

    def get_recipes_count(self, instance):
        return instance.recipes.count()
