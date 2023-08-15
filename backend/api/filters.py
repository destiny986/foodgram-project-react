'''
from django_filters.rest_framework import DjangoFilterBackend


class IngredientFilter(DjangoFilterBackend):
    ...

class DjangoIngredientsFilter(DjangoFilterBackend):
    filterset_class = IngredientFilter
'''