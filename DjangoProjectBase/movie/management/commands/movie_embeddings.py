import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Generate and store embeddings for all movies in the database"

    def handle(self, *args, **kwargs):
        # Load OpenAI API key
        load_dotenv('openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        # Fetch all movies from the database
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in the database")

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        success = 0
        fail = 0
        skipped = 0

        for movie in movies:
            if not movie.description:
                self.stderr.write(f"Skipping '{movie.title}': no description")
                skipped += 1
                continue
            try:
                emb = get_embedding(movie.description)
                movie.emb = emb.tobytes()
                movie.save()
                success += 1
                self.stdout.write(self.style.SUCCESS(f"Embedding stored for: {movie.title}"))
            except Exception as e:
                fail += 1
                self.stderr.write(f"Failed to generate embedding for {movie.title}: {e}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished generating embeddings: {success} stored, {fail} failed, {skipped} skipped (no description)."
            )
        )
