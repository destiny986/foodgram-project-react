from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredient, Favorite, ShoppingList


class IngredientAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in YOURMODEL._meta.get_fields()]
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'image', 'text', 'cooking_time', 'pub_date')
    search_fields = ('tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time', 'pub_date')
    list_filter = ('tags', 'author', 'ingredients', 'name', 'image', 'text', 'cooking_time', 'pub_date')
    empty_value_display = '-пусто-'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient', 'amount')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe', 'add_date')
    search_fields = ('user', 'recipe', 'add_date')
    list_filter = ('user', 'recipe', 'add_date')


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
