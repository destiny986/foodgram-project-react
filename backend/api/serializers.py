from djoser.serializers import UserCreateSerializer, UserSerializer, ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField, UniqueTogetherValidator
from django.shortcuts import get_object_or_404

from recipes.models import Recipe, Tag
from users.models import User, Follow
from recipes.models import Ingredient


# ================================================================================================================
#               User
# ================================================================================================================


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class UserGetSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, author):
        request_user = self.context['request'].user
        return request_user.is_authenticated and Follow.objects.filter(user=request_user, author=author).exists()


# ================================================================================================================
#               Follow
# ================================================================================================================


class FollowRecipeSerializer(ModelSerializer):
# Краткий серик, в фоллоу вызывается
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(ModelSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()     # посчитаем количество рецептов того пользователя на которого подписан
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, author):
        return author.recipes.count()
    
    def get_is_subscribed(self, author):
        request_user = self.context['request'].user
        return request_user.is_authenticated and Follow.objects.filter(user=request_user, author=author).exists()
    
    def get_recipes(self, author):
        request = self.context['request']
        limit = request.query_params.get('recipes_limit')           # вернет none если нет параметра
        if limit is None:
            recipes = author.recipes.all()
        else:
            try:
                limit = int(limit)
                recipes = author.recipes.all()[:limit]
            except:
                recipes = author.recipes.all()
        return FollowRecipeSerializer(recipes, many=True).data


class FollowCreateDeleteSerializer(ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны'
            )
        ]
 
    def validate(self, data):
        if data['user'] == data['author']:
            raise ValidationError('Нельзя подписаться на самого себя')
        return data
    
    # дочерний
    def to_representation(self, instance):
        request = self.context.get('request')
        author = instance['author']
        return FollowSerializer(author, context={'request': request}).data

# OrderedDict([('user', <User: destiny986>), ('author', <User: test1>)])


# ================================================================================================================
#               Ingredient
# ================================================================================================================


class IngredientsSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
