import os
import csv
from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Update movie descriptions in the database from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='updated_movie_descriptions.csv',
            help='Path to the CSV file with updated movie descriptions',
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv']

        if not os.path.exists(csv_file):
            self.stderr.write(self.style.ERROR(f"CSV file not found: {csv_file}"))
            return

        updated = 0
        not_found = 0

        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('Title', '').strip()
                description = row.get('Updated Description', '').strip()

                if not title:
                    continue

                try:
                    movie = Movie.objects.get(title=title)
                    movie.description = description
                    movie.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated: {title}"))
                    updated += 1
                except Movie.DoesNotExist:
                    self.stderr.write(f"Movie not found in DB: {title}")
                    not_found += 1
                except Exception as e:
                    self.stderr.write(f"Error updating '{title}': {str(e)}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished: {updated} movies updated, {not_found} not found in DB."
            )
        )
