import os
import requests
from openai import OpenAI
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Generate an image with OpenAI DALL-E and update the first movie's image field"

    def handle(self, *args, **kwargs):
        # Load environment variables from the .env file
        load_dotenv('openAI.env')

        # Initialize the OpenAI client with the API key
        client = OpenAI(
            api_key=os.environ.get('openai_apikey'),
        )

        # Folder to save images
        images_folder = 'media/movie/images/'
        os.makedirs(images_folder, exist_ok=True)

        # Fetch only the first movie
        movie = Movie.objects.first()
        if not movie:
            self.stderr.write("No movies found in the database.")
            return

        try:
            image_relative_path = self.generate_and_download_image(client, movie.title, images_folder)

            movie.image = image_relative_path
            movie.save()
            self.stdout.write(self.style.SUCCESS(f"Saved and updated image for: {movie.title}"))

        except Exception as e:
            self.stderr.write(f"Failed for {movie.title}: {e}")

        self.stdout.write(self.style.SUCCESS("Process finished (only first movie updated)."))

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

        # Prepare safe filename
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in movie_title)
        image_filename = f"m_{safe_title}.png"
        image_path_full = os.path.join(save_folder, image_filename)

        # Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        with open(image_path_full, 'wb') as f:
            f.write(image_response.content)

        return os.path.join('movie/images', image_filename)
