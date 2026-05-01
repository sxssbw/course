import csv
from django.core.management.base import BaseCommand
from diary.models import Product

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        file_path = options['csv_file']
        created = 0
        updated = 0

        with open(file_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name'].strip()
                if not name:
                    continue  

                product, was_created = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        'calories': float(row['calories']),
                        'proteins': float(row['proteins']),
                        'fats': float(row['fats']),
                        'carbs': float(row['carbs']),
                        'is_custom': False,
                        # created_by не трогаем — это общая база
                    }
                )

                if was_created:
                    created += 1
                else:
                    updated += 1