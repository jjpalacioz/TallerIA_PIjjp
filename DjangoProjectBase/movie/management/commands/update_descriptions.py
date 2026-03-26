import os
from openai import OpenAI
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Update movie descriptions using OpenAI API"

    def handle(self, *args, **kwargs):
        # Load environment variables from the .env file
        load_dotenv('openAI.env')

        # Initialize the OpenAI client with the API key
        client = OpenAI(
            api_key=os.environ.get('openai_apikey'),
        )

        # Helper function to send prompt and get completion from OpenAI
        def get_completion(prompt, model="gpt-3.5-turbo"):
            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content.strip()

        # Instruction to guide the AI response
        instruction = (
            "Vas a actuar como un aficionado del cine que sabe describir de forma clara, "
            "concisa y precisa cualquier película en menos de 200 palabras. La descripción "
            "debe incluir el género de la película y cualquier información adicional que sirva "
            "para crear un sistema de recomendación."
        )

        # Fetch only the first movie from the database
        movie = Movie.objects.first()
        if not movie:
            self.stderr.write("No movies found in the database.")
            return

        self.stdout.write(f"Processing: {movie.title}")
        try:
            prompt = (
                f"{instruction} "
                f"Vas a actualizar la descripción '{movie.description}' de la película '{movie.title}'."
            )

            self.stdout.write(f"Title: {movie.title}")
            self.stdout.write(f"Original Description: {movie.description}")

            updated_description = get_completion(prompt)

            self.stdout.write(f"Updated Description: {updated_description}")

            movie.description = updated_description
            movie.save()

            self.stdout.write(self.style.SUCCESS(f"Updated: {movie.title}"))

        except Exception as e:
            self.stderr.write(f"Failed for {movie.title}: {str(e)}")
