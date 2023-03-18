import base64
from collections import OrderedDict

from django.core.files.base import ContentFile
from rest_framework import serializers
from users.models import Subscription, User

from content.models import (Favorites, IngridientRecipe, Recipe,
                     Shopping_cart, Ingridient, Tags)


class AuthorRecipeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, instance):
        try:
            Subscription.objects.get(followed=instance)
            return True
        except Subscription.DoesNotExist:
            return False


class IngredientsRecipeSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField('amount_info')

    def amount_info(self, instance):
        amounts = (instance.ingredient_amount.values_list('amount', flat=True))
        return ((list(amounts))[0])

    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagsRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class IngridientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridient
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr),
                               name='recipe_image.' + ext)
        return super().to_internal_value(data)


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = AuthorRecipeSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()

    def get_is_favorited(self, instance):
        return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'cooking_time', 'image', 'is_favorited')

    def create(self, validated_data):
        image = validated_data.get('image')
        recipe_author = validated_data.get('author')
        recipe_tags_id = validated_data.get('tags')
        recipe_name = validated_data.get('name')
        recipe_text = validated_data.get('text')
        recipe_cooking_time = validated_data.get('cooking_time')
        recipe_ingredients = self.context.get('request').data['ingredients']
        recipe = Recipe(author=recipe_author, name=recipe_name,
                        text=recipe_text, cooking_time=recipe_cooking_time,
                        image=image)
        recipe.save()

        # обработка данных связанной модели Tags
        for tag in recipe_tags_id:
            # валидация наличия тега в числе предустановленных
            if Tags.objects.filter(id=tag.id).exists():
                # запись ссылок на теги нового рецепта в таблицу through M2M
                Recipe.tags.through.objects.create(recipe_id=recipe.id,
                                                   tags_id=tag.id)
        # обработка данных связанной модели IngridientRecipe
        for ingridient in recipe_ingredients:
            # валидация наличия ингридиента в БД
            if Ingridient.objects.filter(id=(list(ingridient.values())[0])).\
                                         exists():
                # запись ссылок на ингридиенты нового
                # рецепта в таблицу through M2M
                IngridientRecipe.objects.create(ingredient_id=ingridient['id'],
                                                recipe_id=recipe.id,
                                                amount=ingridient['amount'])
        return recipe

    # переопределение структуры поля tags в response
    def to_representation(self, instance):
        rep = OrderedDict(super(RecipeCreateSerializer, self).
                          to_representation(instance))
        tags_id_list = rep['tags']
        tags = []
        for tag_id in tags_id_list:
            x = ((Tags.objects.get(pk=tag_id).__dict__))
            del x['_state']
            tags.append(x)
        rep['tags'] = tags
        rep['is_in_shopping_cart'] = False
        return rep


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorRecipeSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializer(many=True)
    tags = TagsRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, instance):
        try:
            (Favorites.objects.get(favorite_recipe_id=(instance.pk)))
            return True
        except Favorites.DoesNotExist:
            return False

    def get_is_in_shopping_cart(self, instance):
        try:
            Shopping_cart.objects.get(recipe_to_shop=instance.id)
            return True
        except Shopping_cart.DoesNotExist:
            return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'cooking_time', 'image', 'is_favorited',
                  'is_in_shopping_cart')


class IngridientsRecipePatchSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор при запросе PATCH /recipes/{id}/"""
    amount = serializers.SerializerMethodField()

    def get_amount(self, instance):
        amounts = list(instance.ingredient_amount
                       .values_list('amount', flat=True))[0]
        return amounts

    # валидация ингридиентов
    def to_internal_value(self, data):
        try:
            Ingridient.objects.get(pk=(data['id']))
        except Ingridient.DoesNotExist:
            raise serializers.ValidationError("Ингридиента с таким"
                                              "'id' нет в базе")

        if int(data['amount']) >= 1:
            return data
        else:
            raise serializers.ValidationError('Количество ингридиента '
                                              'д.б. больше 0')

    class Meta:
        model = Ingridient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagsRecipePatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        try:
            Tags.objects.filter(id=data).exists()
            return data
        except Tags.DoesNotExist:
            raise serializers.ValidationError("Такого тега нет в базе")


class RecipePatchSerializer(serializers.ModelSerializer):
    ingredients = IngridientsRecipePatchSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    author = AuthorRecipeSerializer(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagsRecipePatchSerializer(many=True)

    def get_is_favorited(self, instance):
        try:
            Favorites.objects.get(favorite_recipe_id=(instance.pk))
            return True
        except Favorites.DoesNotExist:
            return False

    def get_is_in_shopping_cart(self, instance):
        try:
            Shopping_cart.objects.get(recipe_to_shop=instance.id)
            return True
        except Shopping_cart.DoesNotExist:
            return False

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'text',
                  'cooking_time', 'image', 'is_favorited',
                  'is_in_shopping_cart')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        Recipe.tags.through.objects.filter(recipe_id=instance.id).delete()
        IngridientRecipe.objects.filter(recipe_id=instance.id).delete()
        for ingredient in validated_data.get('ingredients'):
            IngridientRecipe.objects.create(ingredient_id=ingredient['id'],
                                            recipe_id=instance.id,
                                            amount=ingredient.get('amount'))
        for tag in validated_data['tags']:
            Recipe.tags.through.objects.create(recipe_id=instance.id,
                                               tags_id=tag)

        instance.save()
        return instance


class ShoppingCartSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def create(self, validated_data):
        (Shopping_cart.objects.create(user_id=self.context.get('user'),
                                      recipe_to_shop_id=self.context.
                                      get('recipe_to_shop')))
        return Recipe.objects.get(id=self.context.get('recipe_to_shop'))


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorites
        fields = ('user', 'favorite_recipe')

    def create(self, validated_data):
        favorite = Favorites(user=validated_data.get('user'),
                             favorite_recipe=validated_data.
                             get('favorite_recipe'))
        favorite.save()
        return favorite

    def to_representation(self, instance):
        image = Recipe.objects.get(id=instance.favorite_recipe_id).image.url
        id = instance.favorite_recipe_id
        time = Recipe.objects.get(id=instance.favorite_recipe_id).cooking_time
        name = Recipe.objects.get(id=instance.favorite_recipe_id).name
        return {'id': id, 'name': name, 'cooking_time': time, 'image': image}
