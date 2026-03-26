import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Compare two movies and optionally a prompt using OpenAI embeddings and cosine similarity"

    def add_arguments(self, parser):
        parser.add_argument(
            '--movie1',
            type=str,
            default=None,
            help='Title of the first movie to compare (default: first movie in DB)',
        )
        parser.add_argument(
            '--movie2',
            type=str,
            default=None,
            help='Title of the second movie to compare (default: second movie in DB)',
        )
        parser.add_argument(
            '--prompt',
            type=str,
            default='película de aventuras y acción',
            help='Prompt to compare against the movies',
        )

    def handle(self, *args, **kwargs):
        # Load OpenAI API key
        load_dotenv('openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # Get the two movies to compare
        title1 = kwargs.get('movie1')
        title2 = kwargs.get('movie2')
        prompt = kwargs.get('prompt')

        try:
            if title1:
                movie1 = Movie.objects.get(title=title1)
            else:
                movie1 = Movie.objects.filter(description__isnull=False).exclude(description='').first()

            if title2:
                movie2 = Movie.objects.get(title=title2)
            else:
                movies_with_desc = Movie.objects.filter(description__isnull=False).exclude(description='')
                movie2 = movies_with_desc.exclude(id=movie1.id).first()

        except Movie.DoesNotExist as e:
            self.stderr.write(f"Movie not found: {e}")
            return

        if not movie1 or not movie2:
            self.stderr.write("Not enough movies with descriptions in the database.")
            return

        self.stdout.write(f"\nComparing: '{movie1.title}' vs '{movie2.title}'")

        # Generate embeddings
        self.stdout.write(f"Generating embedding for: {movie1.title}")
        emb1 = get_embedding(movie1.description)

        self.stdout.write(f"Generating embedding for: {movie2.title}")
        emb2 = get_embedding(movie2.description)

        # Print embedding info for movie1
        self.stdout.write(f"\n🎬 Embedding generado para '{movie1.title}':")
        self.stdout.write(f"   Dimensiones: {emb1.shape}")
        self.stdout.write(f"   Primeros 5 valores: {emb1[:5]}")

        # Compute similarity between movies
        similarity = cosine_similarity(emb1, emb2)
        self.stdout.write(
            f"\n🎬 Similaridad entre '{movie1.title}' y '{movie2.title}': {similarity:.4f}"
        )

        # Compare against a prompt
        self.stdout.write(f"\nGenerating embedding for prompt: '{prompt}'")
        prompt_emb = get_embedding(prompt)

        sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
        sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

        self.stdout.write(f"📝 Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}")
        self.stdout.write(f"📝 Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}")

        if sim_prompt_movie1 > sim_prompt_movie2:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Recomendación para '{prompt}': {movie1.title} (similitud: {sim_prompt_movie1:.4f})"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ Recomendación para '{prompt}': {movie2.title} (similitud: {sim_prompt_movie2:.4f})"
                )
            )
