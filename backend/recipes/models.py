from django.core.exceptions import ValidationError
from django.db import models

from users.models import User


class NameField(models.CharField):
    """Будем сохранять в lowercase все NameField."""

    def get_prep_value(self, value):
        return str(value).lower()


def positive_not_zero(value):
    """Проверка на уровне модели (для админки)."""
    if value <= 0:
        raise ValidationError(
            ("Значение должно быть не меньше 1"),
            params={"value": value},
        )


class Ingredient(models.Model):
    name = NameField(
        "Название ингредиента",
        max_length=255,
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=255,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("name", "measurement_unit"), name="unique_ingredient"
            ),
        )
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = NameField("Название тега", max_length=255, unique=True)
    color = models.CharField("Цвет", max_length=255, unique=True)
    slug = models.SlugField("Тег", max_length=255, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тег",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиент",
    )
    name = models.CharField(
        "Название рецепта",
        max_length=255,
    )
    image = models.ImageField(
        "Картинка",
        upload_to="recipe_images/",
        blank=True,
        null=True,
    )
    text = models.TextField(
        "Описание",
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления (минуты)", validators=(positive_not_zero,)
    )
    pub_date = models.DateTimeField(
        "Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients_in_recipes",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipes_for_ingredient",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество", validators=(positive_not_zero,)
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"
        constraints = (
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_ingredient_in_recipe",
            ),
        )

    def __str__(self):
        return (
            f"{self.ingredient.name} -"
            f" {self.amount} {self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Избранные рецепты",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite"
            ),
        )
        verbose_name = "Избранное"

    def __str__(self):
        return f"{self.recipe.name} в избраннном у {self.user.username}"


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shoppinglist",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shoppinglist",
        verbose_name="Рецепт в листе покупок",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_recipe_in_shoppinglist",
            ),
        )
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return f"{self.recipe.name} в списке покупок {self.user.username}"
