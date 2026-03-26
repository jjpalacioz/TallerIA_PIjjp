import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Assign pre-generated images from the images folder to each movie in the database"

    def handle(self, *args, **kwargs):
        # ✅ Folder where pre-generated images are stored
        images_folder = 'media/movie/images/'

        if not os.path.exists(images_folder):
            self.stderr.write(f"Images folder '{images_folder}' not found. Please add the images first.")
            return

        # ✅ Fetch all movies from the database
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in the database")

        updated_count = 0

        for movie in movies:
            # ✅ Build the expected image filename based on the movie title
            image_filename = f"m_{movie.title}.png"
            image_path_full = os.path.join(images_folder, image_filename)

            if os.path.exists(image_path_full):
                # ✅ Relative path to store in the database
                image_relative_path = os.path.join('movie/images', image_filename)
                movie.image = image_relative_path
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"Image not found for: {movie.title} (expected: {image_path_full})"))

        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movies with images from folder."))
