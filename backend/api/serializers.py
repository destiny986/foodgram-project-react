from djoser.serializers import UserCreateSerializer, UserSerializer, ValidationError
from rest_framework.serializers import ModelSerializer, SerializerMethodField, UniqueTogetherValidator, IntegerField, CharField, ImageField, PrimaryKeyRelatedField
from django.shortcuts import get_object_or_404
import base64
from django.core.files.base import ContentFile

from recipes.models import Recipe, Tag, RecipeIngredient
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


# ================================================================================================================
#               Tag
# ================================================================================================================


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


# ================================================================================================================
#               Recipe
# ================================================================================================================

#               GET

class RecipeIngredientGetSerializer(ModelSerializer):  # передал в него RecipeIngredient
    id = IntegerField(source='ingredient.id')
    name = CharField(source='ingredient.name')
    measurement_unit = CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount', )


class RecipeGetSerializer(ModelSerializer):         # передал в него рецепт
    tags = TagSerializer(many=True)
    author = UserGetSerializer()
    ingredients = RecipeIngredientGetSerializer(many=True, source='ingredients_in_recipes') # все RecipeIngredient в которых есть этот recipe

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time')


#               POST


class RecipeIngredientPostSerializer(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

class RecipePostSerializer(ModelSerializer):
    ingredients = RecipeIngredientPostSerializer(many=True, source='ingredients_in_recipes')
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')


    def create(self, validated_data):
        print('=================================================')
        print(validated_data)
        print('=================================================')
        ingredients = validated_data.pop('ingredients_in_recipes')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user

        # To create and save an object in a single step, use the create() method
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient.get('id'))
            amount = ingredient.get('amount')
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient_obj, amount=amount)
        recipe.save()

        return recipe


    def update(self, instance, validated_data):

        new_tags = validated_data.pop('tags')
        instance.tags.clear()
        for tag in new_tags:
            tag_obj = get_object_or_404(Tag, id=tag.id)
            instance.tags.add(tag_obj)

        new_ingredients = validated_data.pop('ingredients_in_recipes')
        instance.ingredients.clear()
        for ingredient in new_ingredients:
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient.get('id'))
            amount = ingredient.get('amount')
            instance.ingredients.add(ingredient_obj, through_defaults={'amount': amount})

        super().update(instance, validated_data)        # name, image, text, cooking_time

        instance.save()
        return instance


    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetSerializer(instance, context={'request': request}).data
