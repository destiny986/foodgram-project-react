# Generated by Django 3.2 on 2023-08-16 17:12

from django.db import migrations, models
import recipes.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_auto_20230814_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[recipes.models.positive_not_zero], verbose_name='Время приготовления (минуты)'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[recipes.models.positive_not_zero], verbose_name='Количество'),
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_ingredient_in_recipe'),
        ),
    ]