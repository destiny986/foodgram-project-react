from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet, ViewSet
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters2
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Sum
from django.shortcuts import HttpResponse
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import FilterSet, ModelMultipleChoiceFilter, BooleanFilter

from .permissions import CustomPermission
from .serializers import FollowSerializer, FollowCreateDeleteSerializer, IngredientsSerializer, TagSerializer, RecipeGetSerializer, RecipePostSerializer, FavoriteSerializer, ShoppingListSerializer
from users.models import Follow, User
from recipes.models import Ingredient, Tag, Recipe, Favorite, ShoppingList, RecipeIngredient


# ================================================================================================================
#               Follow
# ================================================================================================================


# IsAuthenticated default
class FollowViewSet(ReadOnlyModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)   # <===== self.request.user.follower.all()


class FollowUserViewSet(UserViewSet):
    @action(detail=True, methods=['post'], name='Create follow')
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])               # проверит на наличие автора
        serializer = FollowCreateDeleteSerializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @subscribe.mapping.delete
    def destroy(self, request, *args, **kwargs):
        following_id = self.kwargs.get('id')
        object = get_object_or_404(Follow, user=request.user, author=following_id)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ================================================================================================================
#               Ingredient
# ================================================================================================================


'''
# https://stackoverflow.com/questions/45296939/how-can-i-create-a-partial-search-filter-in-django-rest-framework
class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)

class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    # https://django-filter.readthedocs.io/en/latest/guide/rest_framework.html#adding-a-filterset-with-filterset-class
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    pagination_class = None
    filterset_class  = IngredientFilter
    # search_fields = ('name',)
    # ordering_fields = ('name',)
    ordering = ('name',)
'''

# https://www.django-rest-framework.org/api-guide/filtering/#searchfilter
class IngredientFilter(SearchFilter):
    search_param = 'name'


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    pagination_class = None
    search_fields = ['^name',]  # '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
                                # '$' Regex search.


# ================================================================================================================
#               Tags
# ================================================================================================================


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


# ================================================================================================================
#               Recipes
# ================================================================================================================

#############################################################################################
#############################################################################################
#############################################################################################
#############################################################################################
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
class RecipeFilterSet(FilterSet):
    is_favorited = BooleanFilter(method='get_is_favorited')     # value - True/False
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')
    tags = ModelMultipleChoiceFilter(queryset=Tag.objects.all(), field_name='tags__slug', to_field_name='slug')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def get_is_favorited(self, queryset, name, value):
        if value == True:
            return Recipe.objects.filter(favorites__user=self.request.user)
        return Recipe.objects.exclude(favorites__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value == True:
            return Recipe.objects.filter(shoppinglist__user=self.request.user)
        return Recipe.objects.exclude(shoppinglist__user=self.request.user)
    
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#############################################################################################
#############################################################################################
#############################################################################################
#############################################################################################

class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (CustomPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, methods=['post'], name='Create favorite')
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        favorite = get_object_or_404(Favorite, user=request.user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ==============================================================================================

    @action(detail=True, methods=['post'], name='Take recipe to shopping list')
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        serializer = ShoppingListSerializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        ShoppingList.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        shoppinglist = get_object_or_404(ShoppingList, user=request.user, recipe=recipe)
        shoppinglist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    # CustomPermission тут, чтение всем разрешено
    @action(detail=False, methods=['get'], name='Download shopping list', permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request, *args, **kwargs):
        
        # https://stackoverflow.com/questions/69426522/aggregate-sum-in-django-sum-of-objects-with-the-same-name
        shopping_list = RecipeIngredient.objects.filter(
            recipe__shoppinglist__user=request.user).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by()

        result = ['Список покупок:\n',]
        for ingredient in shopping_list:
            string = ' '.join(str(i) for i in list(ingredient.values()))
            result.append(f'\n{string}')

        response = HttpResponse(result, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response
