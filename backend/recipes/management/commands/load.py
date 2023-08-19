import csv
from django.core.management import BaseCommand

from recipes.models import Ingredient


# python manage.py load --path ../data/ingredients.csv
class Command(BaseCommand):
    help = 'Загружает ингредиенты'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        with open(path, 'rt', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                Ingredient.objects.create(
                    name=row[0],
                    measurement_unit=row[1],
                )
        print('Загрузка завершена')
