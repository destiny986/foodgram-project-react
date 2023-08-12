from djoser.serializers import UserCreateSerializer, UserSerializer, ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField, UniqueTogetherValidator

from recipes.models import Recipe
from users.models import User, Follow

class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')


class UserGetSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


# ================================================================================================================


class FollowRecipeSerializer(ModelSerializer):
# Краткий серик, в фоллоу вызывается
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(ModelSerializer):
    recipes = FollowRecipeSerializer(many=True)
    recipes_count = SerializerMethodField()     # посчитаем количество рецептов того пользователя на которого подписан

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):           # obj == User
        return obj.recipes.count()


class FollowCreateDeleteSerializer(ModelSerializer):
    class Meta:
        # extra_kwargs = {'user': {'required': False}, 'author': {'required': False}}
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
            raise ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data
    

# ================================================================================================================