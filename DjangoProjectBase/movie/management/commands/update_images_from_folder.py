import os
import requests
from openai import OpenAI
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Generate images with OpenAI DALL-E for all movies and update image fields"

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            default='media/movie/images/',
            help='Folder where images will be saved',
        )

    def handle(self, *args, **kwargs):
        # Load environment variables from the .env file
        load_dotenv('openAI.env')

        # Initialize the OpenAI client with the API key
        client = OpenAI(
            api_key=os.environ.get('openai_apikey'),
        )

        images_folder = kwargs['folder']
        os.makedirs(images_folder, exist_ok=True)

        movies = Movie.objects.all()
        total = movies.count()
        self.stdout.write(f"Found {total} movies. Generating images...")

        success_count = 0
        fail_count = 0

        for movie in movies:
            try:
                image_relative_path = self.generate_and_download_image(
                    client, movie.title, images_folder
                )
                movie.image = image_relative_path
                movie.save()
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"[{success_count}/{total}] Updated image for: {movie.title}")
                )
            except Exception as e:
                fail_count += 1
                self.stderr.write(f"Failed for '{movie.title}': {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished: {success_count} images updated, {fail_count} failed."
            )
        )

    def generate_and_download_image(self, client, movie_title, save_folder):
        """
        Generates an image using OpenAI's DALL-E model and downloads it.
        Returns the relative image path or raises an exception.
        """
        prompt = f"Movie poster of {movie_title}"

        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="256x256",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in movie_title)
        image_filename = f"m_{safe_title}.png"
        image_path_full = os.path.join(save_folder, image_filename)

        image_response = requests.get(image_url)
        image_response.raise_for_status()
        with open(image_path_full, 'wb') as f:
            f.write(image_response.content)

        return os.path.join('movie/images', image_filename)
