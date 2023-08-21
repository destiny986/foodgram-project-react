from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "measurement_unit")
    search_fields = ("name", "measurement_unit")
    list_filter = ("name", "measurement_unit")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "color", "slug")
    search_fields = ("name", "color", "slug")
    list_filter = ("name", "color", "slug")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "author",
        "name",
        "image",
        "text",
        "cooking_time",
        "pub_date",
    )
    search_fields = (
        "tags",
        "author",
        "ingredients",
        "name",
        "image",
        "text",
        "cooking_time",
        "pub_date",
    )
    list_filter = (
        "tags",
        "author",
        "ingredients",
        "name",
        "image",
        "text",
        "cooking_time",
        "pub_date",
    )
    empty_value_display = "-пусто-"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "recipe", "ingredient", "amount")
    search_fields = ("recipe", "ingredient", "amount")
    list_filter = ("recipe", "ingredient", "amount")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "recipe")
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe")
