import csv
import os

from django.core.management import BaseCommand

from api.models import Ingridient


class Command(BaseCommand):
    """Отдельный модуль загрузки ингридентов из данного файла"""

    DEFAULT_PATH = os.path.join(os.path.
                                abspath('static/data'), 'ingredients.csv')

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path', type=str, nargs='?', default=self.DEFAULT_PATH
        )

    def handle(self, *args, **options):
        with open('api/data/ingredients.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                name, unit = row
                Ingridient.objects.get_or_create(
                    name=name, measurement_unit=unit
                )
        self.stdout.write(
            self.style.SUCCESS('Done successfully')
        )
