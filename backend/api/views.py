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

from .serializers import FollowSerializer, FollowCreateDeleteSerializer, IngredientsSerializer, TagSerializer
from users.models import Follow, User
from recipes.models import Ingredient, Tag


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
    filter_backends = (DjangoFilterBackend, OrderingFilter, IngredientFilter)
    pagination_class = None
    search_fields = ['^name',]  # '@' Full-text search. (Currently only supported Django's PostgreSQL backend.)
                                # '$' Regex search.
    ordering = ('name',)

