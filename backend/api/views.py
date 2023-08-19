from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import (
    BooleanFilter,
    DjangoFilterBackend,
    FilterSet,
    ModelMultipleChoiceFilter,
)
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)
from users.models import Follow, User

from .permissions import CustomPermission
from .serializers import (
    FavoriteSerializer,
    FollowCreateDeleteSerializer,
    FollowSerializer,
    IngredientsSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    ShoppingListSerializer,
    TagSerializer,
)

# ===========================================================================
#               Follow
# ===========================================================================


class FollowViewSet(ReadOnlyModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class FollowUserViewSet(UserViewSet):
    @action(detail=True, methods=["post"], name="Create follow")
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=kwargs["id"])
        serializer = FollowCreateDeleteSerializer(
            data={"user": request.user.id, "author": author.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        Follow.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def destroy(self, request, *args, **kwargs):
        following_id = self.kwargs.get("id")
        object = get_object_or_404(
            Follow, user=request.user, author=following_id
        )
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===========================================================================
#               Ingredient
# ===========================================================================


class IngredientFilter(SearchFilter):
    """Фильтр для поиска ингредиента по имени."""

    search_param = "name"


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    pagination_class = None
    search_fields = [
        "^name",
    ]


# ===========================================================================
#               Tags
# ===========================================================================


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


# ===========================================================================
#               Recipes
# ===========================================================================


class RecipeFilterSet(FilterSet):
    """Доп. фильтр для рецептов."""

    is_favorited = BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = BooleanFilter(method="get_is_in_shopping_cart")
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug",
    )

    class Meta:
        model = Recipe
        fields = ("is_favorited", "is_in_shopping_cart", "author", "tags")

    def get_is_favorited(self, queryset, name, value):
        if value == True:
            return Recipe.objects.filter(favorites__user=self.request.user)
        return Recipe.objects.exclude(favorites__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value == True:
            return Recipe.objects.filter(shoppinglist__user=self.request.user)
        return Recipe.objects.exclude(shoppinglist__user=self.request.user)


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (CustomPermission,)
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, methods=["post"], name="Create favorite")
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
        serializer = FavoriteSerializer(
            data={"user": request.user.id, "recipe": recipe.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        Favorite.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("pk"))
        favorite = get_object_or_404(
            Favorite, user=request.user, recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=["post"], name="Take recipe to shopping list"
    )
    def shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])
        serializer = ShoppingListSerializer(
            data={"user": request.user.id, "recipe": recipe.id},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        ShoppingList.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get("pk"))
        shoppinglist = get_object_or_404(
            ShoppingList, user=request.user, recipe=recipe
        )
        shoppinglist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["get"],
        name="Download shopping list",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        shopping_list = (
            RecipeIngredient.objects.filter(
                recipe__shoppinglist__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
            .order_by()
        )

        result = [
            "Список покупок:\n",
        ]
        for ingredient in shopping_list:
            string = " ".join(str(i) for i in list(ingredient.values()))
            result.append(f"\n{string}")

        response = HttpResponse(result, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_cart.txt"'
        return response
